# Vbox testbed manager imports
from vboxapi import VirtualBoxManager
import time
import traceback

# gevent imports
import gevent
import gevent.monkey
from gevent.lock import BoundedSemaphore

#to reduce stdout
import logging

#catch signal for quitting
import signal
import gc

gevent.monkey.patch_all()

# gevent imports
from gevent.pywsgi import WSGIServer
from flask import Flask
from flask import json
from flask import render_template

probeTime = 5
restoreTime = 1
lockWaitTime = 5

####vars needed for testbed manager threads:
mgr = VirtualBoxManager(None, None)
vbox = mgr.vbox
session = mgr.getSessionObject(vbox)

groupToVms = {}
availableState = []
availableInfo = []
notAvailableState = []
notAvailableInfo = []
restoreState = []
restoreInfo = []
vms = {}

# vars needed for gevent (lock)
sem = BoundedSemaphore(1)

####functions needed for testbed manager threads:
def getVMInfo(session, machine):
    answer = {}
    answer["name"] = str(machine.name)
    answer["groups"] = machine.groups
    answer["vrde"] = machine.VRDEServer.enabled
    answer["vrdeproperty[TCP/Ports]"] = str(machine.VRDEServer.getVRDEProperty('TCP/Ports'))
    answer["VMState"] = machine.state

    # need active machine/console for the following:
    if session.state != mgr.constants.SessionState_Unlocked or machine.state != mgr.constants.MachineState_Running:
        #logging.debug("session is locked or machine is not running, cannot get console (1)"+str(session.state))
        return answer
    #print "mstate",machine.state,"constant",mgr.constants.MachineState_Running,"result",machine.state == mgr.constants.MachineState_Running
    machine.lockMachine(session, mgr.constants.LockType_Shared)
    console = session.console
    if console == None:
        # if can't get console, this means that the vm is probably off
        #logging.debug("cannot get console (2), machine is probably off")
        session.unlockMachine()
        return answer

    answer["VRDEActiveConnection"] = console.VRDEServerInfo.active
    res = console.display.getScreenResolution(0)
    # try to set it to 16 bpp to reduce throughput requirements
    # if res > 16:
    #    logging.debug("Sending hint to adjust resolution")
    #    console.display.setVideoModeHint(0, True, False, 0, 0, 0, 0, 16)
    #    res = console.display.getScreenResolution(0)
    #    logging.debug("After adjustment request"+str(res))
    answer["VideoMode"] = res[2]
    session.unlockMachine()

    return answer


def powerdownMachine(session, machine):
    try:
        if session.state != mgr.constants.SessionState_Unlocked or machine.state != mgr.constants.MachineState_Running:
            logging.debug("session is locked or machine is not running, not powering down")
            return -1
        machine.lockMachine(session, mgr.constants.LockType_Shared)
        console = session.console
        # if can't get console, this means that the vm is probably off
        if console != None:
            logging.debug("Calling Power Down API Function")
            progress = console.powerdown()
            progress.waitForCompletion(-1)
        session.unlockMachine()
        return 0
    except Exception as e:
        logging.error("error during powerdown"+ str(e))
        session.unlockMachine()
        return -1


def restoreMachine(session, machine):
    if session.state != mgr.constants.SessionState_Unlocked or (machine.state != mgr.constants.MachineState_PoweredOff and machine.state != mgr.constants.MachineState_Aborted):
        logging.debug("session is locked or machine is not powered off, not restoring vm. Session State:" + str(session.state) + "Machine State:" + str(machine.state))
        return -1
    try:
        machine.lockMachine(session, mgr.constants.LockType_Shared)
        snap = machine.currentSnapshot
        # have to reference using session for some weird reason!
        logging.debug("Calling Restore API Function")
        progress = session.machine.restoreSnapshot(snap)
        progress.waitForCompletion(-1)
        session.unlockMachine()
        return 0
    except Exception as e:
        logging.error("Error in Restore: " + str(mgr) + " " + str(e))
        traceback.print_exc()
        session.unlockMachine()
        return -1



def startMachine(session, machine):
    try:
        if session.state != mgr.constants.SessionState_Unlocked or machine.state != mgr.constants.MachineState_Saved:
            logging.debug( "session is locked, not starting vm")
            return -1
            logging.debug("Calling Launch API Function")
        progress = machine.launchVMProcess(session, "headless", "")
        progress.waitForCompletion(-1)
        session.unlockMachine()
        return 0
    except Exception as e:
        logging.error("error during start" + str(e))
        session.unlockMachine()
        return -1

def makeAvailableToNotAvailable(vmNameList):
    # print "making notAvailable",vmNameList,"\n"

    for vmName in vmNameList:
        sem.wait()
        sem.acquire()
        availableState.remove(vmName)
        notAvailableState.append(vmName)
        sem.release()


def makeNotAvailableToRestoreState(vmNameList):
    # print "making notAvailableToRestore:",vmNameList,"\n"

    for vmName in vmNameList:
        sem.wait()
        sem.acquire()
        notAvailableState.remove(vmName)
        restoreState.append(vmName)
        sem.release()


def makeRestoreToAvailableState():  # will look at restore buffer and process any items that exist
    global vms
    global groupToVms
    restoreSubstates = {}
    while True:
        # print "making restoreToAvailable:",vmNameList,"\n"
        try:
            # Need to reload all vms that are in the group of the vm in the "restore" state
            # get each vm in restoreState list
            for vmToRestore in restoreState:
                # if this vm has a group
                logging.debug("vmToRestore" + str(vmToRestore))
                if vmToRestore in vms and "groups" in vms[vmToRestore]:
                    # get all vms in group
                    groupToRestore = str(vms[vmToRestore]["groups"][0])
                    logging.debug("groupToRestore" + str(groupToRestore))
                    # add each vm in group to restoreSubstate list (if haven't already)
                    for vmInGroup in groupToVms[groupToRestore]:
                        logging.debug("vmInGroup" + str(vmInGroup))
                        if vmInGroup not in restoreSubstates:
                            restoreSubstates[vmInGroup] = "pending"
                            # Process next stage in restore

            logging.debug("Restore substates:"+str(restoreSubstates))
            vmsToRemoveFromQueue = []
            for substate in restoreSubstates:
                logging.debug("Processing state for:"+str(substate)+str(restoreSubstates[substate]))
                sem.wait()
                sem.acquire()
                mach = vbox.findMachine(substate)
                vmState = getVMInfo(session, mach)["VMState"]
                sem.release()
                logging.debug("currState:" + str(vmState))
                result = -1
                if restoreSubstates[substate] == "pending" and vmState == mgr.constants.MachineState_Running:
                    logging.debug("CALLING POWEROFF"+str(substate)+":"+str(restoreSubstates[substate]))
                    result = powerdownMachine(session, mach)
                    if result != -1:
                        restoreSubstates[substate] = "poweroff_sent"

                elif restoreSubstates[substate] == "poweroff_sent" and vmState == mgr.constants.MachineState_PoweredOff or vmState == mgr.constants.MachineState_Aborted:
                    logging.debug("CALLING RESTORE"+str(substate)+":"+str(restoreSubstates[substate]))
                    result = restoreMachine(session, mach)
                    if result != -1:
                        restoreSubstates[substate] = "restorecurrent_sent"

                elif restoreSubstates[
                    substate] == "restorecurrent_sent" and vmState == mgr.constants.MachineState_Saved:
                    logging.debug("CALLING STARTVM"+str(substate)+":"+str(restoreSubstates[substate]))
                    result = startMachine(session, mach)
                    if result != -1:
                        restoreSubstates[substate] = "startvm_sent"
                elif restoreSubstates[substate] == "startvm_sent" and vmState == mgr.constants.MachineState_Running:
                    restoreSubstates[substate] = "complete"
                    sem.wait()
                    sem.acquire()
                    if substate in restoreState:
                        # remove from restore so it can be added to available buffer once again
                        restoreState.remove(substate)
                    if substate in notAvailableState:
                        notAvailableState.remove(substate)
                    sem.release()
                    vmsToRemoveFromQueue.append(substate)

            for rem in vmsToRemoveFromQueue:
                if rem in restoreSubstates:
                    del restoreSubstates[rem]
            time.sleep(restoreTime)
        except Exception as e:
            logging.error("RESTORE: An error occured: "+str(e))
            time.sleep(lockWaitTime)
            pass


def makeNewToAvailableState(vmNameList):
    # print "making available:",vmNameList,"\n"
    for vmName in vmNameList:
        sem.wait()
        sem.acquire()
        availableState.append(vmName)
        sem.release()


def manageStates():
    global vms
    global groupToVms
    global availableInfo

    while True:
        try:
            logging.debug("Manage States loop start")
            currvms = {}
            currGroupToVms = {}

            # first get all vms
            for mach in vbox.machines:
                logging.debug("getting info for machine"+str(mach.name))
                # print "MACHINE STATE!!!!!!!",mach.name,mach.state
                currvms[str(mach.name)] = getVMInfo(session, mach)

            # for each vm get info and place in state list
            logging.debug("placing info into state list")
            for vm in currvms:
                # print "VMInfo:",vm,currvms[vm]["groups"],"\n\n"
                # get group name and add this vm to a dictionary of that group:
                for group in currvms[vm]["groups"]:
                    gname = str(group)
                    # print "GROUP Name:",gname
                    if gname != "/":
                        if gname not in currGroupToVms:
                            currGroupToVms[gname] = []
                        currGroupToVms[gname].append(vm)

                        # so we get all at once (may have to create a lock?)
            sem.wait()
            sem.acquire()
            ###lock###
            vms = currvms
            groupToVms = currGroupToVms
            ###unlock###
            sem.release()

            # print "VMS:",vms
            # print "GROUPS:",groupToVms
            ########Assign each vm into a state list############

            # first look at any "not available" to see if they go into the "restore" state
            nasList = []
            for vmName in vms:
                if "VRDEActiveConnection" in vms[vmName]:
                    if vms[vmName]["VRDEActiveConnection"] == 1 and vmName in availableState and vmName not in notAvailableState and vmName not in restoreState:
                        nasList.append(vmName)
                    elif vms[vmName]["VRDEActiveConnection"] == 0 and vmName in notAvailableState and vmName not in restoreState and vmName not in restoreState:
                        restoreState.append(vmName)

            makeAvailableToNotAvailable(nasList)
            # Note that the restore thread will move vms in restore buffer available after processing
            # add any newly available vms into the available buffer
            av = []
            for vmName in vms:
                if "vrde" in vms[vmName] and vms[vmName]["vrde"] == 1 and vms[vmName]["VMState"] == mgr.constants.MachineState_Running:
                    # make available
                    if vmName not in notAvailableState and vmName not in restoreState and vmName not in availableState:
                        av.append(vmName)
            makeNewToAvailableState(av)

            # add available info to available vms
            sem.wait()
            sem.acquire()
            availableInfo = []
            for vmName in availableState:
                if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
                    availableInfo.append((vms[vmName]["name"], vms[vmName]["vrdeproperty[TCP/Ports]"]))
            sem.release()
            availableInfo.sort(key=lambda tup: tup[0])

            # Print out status
            logging.info("\n\n\n")
            logging.info("status:")
            logging.info("available:"+str(availableState))
            logging.info("notAvailable:"+str(notAvailableState))
            logging.info("restore:"+str(restoreState))
            time.sleep(probeTime)

        except Exception as x:
            logging.error("STATES: An error occured:" + str(x))
            time.sleep(lockWaitTime)

app = Flask(__name__)
app.debug = True


# Simple catch-all server
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    return render_template('show_data.html', templateAvailable=availableInfo)

def signal_handler(signal, frame):
    global mgr
    global vbox
    global session
    logging.info("Cleaning up...")
    try:
        logging.info("Killing webserver...")
        httpServer.stop()
        logging.info("Killing threads...")
        gevent.kill(srvGreenlet)
        gevent.kill(stateAssignmentThread)
        gevent.kill(restoreThread)

        logging.info("Removing VirtualBox ISession...")
        del session
        logging.info("Removing IVirtualBox Interface...")
        del vbox
        mgr.deinit()
        logging.info("Removing VirtualBox Manager...")
        del mgr
        logging.info("Collecting Garbage...")
        gc.collect()
        logging.info("Clean up complete. Exitting...")
        exit()
    except Exception as e:
        logging.error("Error during cleanup"+str(e))
        exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    logging.basicConfig(level=logging.DEBUG)

    httpServer = WSGIServer(('0.0.0.0', 8080), app)

    srvGreenlet = gevent.spawn(httpServer.start)
    stateAssignmentThread = gevent.spawn(manageStates)
    restoreThread = gevent.spawn(makeRestoreToAvailableState)

    try:
        gevent.joinall([srvGreenlet, stateAssignmentThread, restoreThread])
    except Exception as e:
        logging.error("An error occured in threads"+str(e))
        exit()
