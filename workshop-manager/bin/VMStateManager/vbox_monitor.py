# Vbox testbed manager imports
from vboxapi import VirtualBoxManager
import time
import traceback

# gevent imports
import gevent
import gevent.monkey
from gevent.lock import BoundedSemaphore
gevent.monkey.patch_all()

#to reduce stdout
import logging

#For cleanup
import gc

probeTime = 5
restoreTime = 1
lockWaitTime = 5

####vars needed for testbed manager threads:
mgr = VirtualBoxManager(None, None)
vbox = mgr.getVirtualBox()
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
queueStateSem = BoundedSemaphore(1)
availableInfoSem = BoundedSemaphore(1)

def getGroupToVms():
    return groupToVms


def getAvailableState():
    return availableState

def getAvailableInfo():
    #availableInfoSem.wait()
    return availableInfo


####functions needed for testbed manager threads:
def getVMInfo(session, machine):
    answer = {}
    answer["name"] = str(machine.name)
    ##Change for XPCOM
    answer["groups"] = mgr.getArray(machine,'groups')
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
            progress = console.powerDown()
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
        queueStateSem.wait()
        queueStateSem.acquire()
        availableState.remove(vmName)
        notAvailableState.append(vmName)
        queueStateSem.release()


def makeNotAvailableToRestoreState(vmNameList):
    # print "making notAvailableToRestore:",vmNameList,"\n"

    for vmName in vmNameList:
        queueStateSem.wait()
        queueStateSem.acquire()
        notAvailableState.remove(vmName)
        restoreState.append(vmName)
        queueStateSem.release()


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
                queueStateSem.wait()
                queueStateSem.acquire()
                mach = vbox.findMachine(substate)
                vmState = getVMInfo(session, mach)["VMState"]
                queueStateSem.release()
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
                    queueStateSem.wait()
                    queueStateSem.acquire()
                    if substate in restoreState:
                        # remove from restore so it can be added to available buffer once again
                        restoreState.remove(substate)
                    if substate in notAvailableState:
                        notAvailableState.remove(substate)
                    queueStateSem.release()
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
        queueStateSem.wait()
        queueStateSem.acquire()
        availableState.append(vmName)
        queueStateSem.release()


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
            ##Change for XPCOM
            for mach in mgr.getArray(vbox,'machines'):
                logging.debug("getting info for machine"+str(mach.name))
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
            queueStateSem.wait()
            queueStateSem.acquire()
            ###lock###
            vms = currvms
            groupToVms = currGroupToVms
            ###unlock###
            queueStateSem.release()

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
            availableInfoSem.wait()
            availableInfoSem.acquire()
            availableInfo = []
            for vmName in availableState:
                if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
                    availableInfo.append((vms[vmName], "Available"))
            for vmName in notAvailableState:
                if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
                    # availableInfo.append((vms[vmName]["groups"][0], vms[vmName]["name"], vms[vmName]["vrdeproperty[TCP/Ports]"]))
                    availableInfo.append((vms[vmName], "Not available"))
            for vmName in restoreState:
                if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
                    # availableInfo.append((vms[vmName]["groups"][0], vms[vmName]["name"], vms[vmName]["vrdeproperty[TCP/Ports]"]))
                    availableInfo.append((vms[vmName], "Restoring"))
            #availableInfo.sort(key=lambda tup: tup[0]["name"])
            availableInfoSem.release()

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

def cleanup():
    global mgr
    global vbox
    global session
    logging.info("Cleaning up VBOX_MONITOR...")
    try:
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

    except Exception as e:
        logging.error("Error during cleanup"+str(e))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    stateAssignmentThread = gevent.spawn(manageStates)
    restoreThread = gevent.spawn(makeRestoreToAvailableState)

    try:
        gevent.joinall([stateAssignmentThread, restoreThread])
    except Exception as e:
        logging.error("An error occured in threads"+str(e))
        cleanup()
