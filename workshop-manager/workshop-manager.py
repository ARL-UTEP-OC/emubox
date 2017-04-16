#Vbox testbed manager imports
from vboxapi import VirtualBoxManager
import subprocess
import shutil
import xml.etree.ElementTree as ET
import shlex
import time
import traceback

#gevent imports
import gevent
import gevent.monkey
from gevent.lock import BoundedSemaphore

gevent.monkey.patch_all()

#gevent imports
from gevent.pywsgi import WSGIServer
from flask import Flask
from flask import json
from flask import render_template

sleepTime = 10
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
#itemsOfInterest: ["name", "groups", "vrde", "VRDEActiveConnection", "VideoMode",\
#  "vrdeproperty[TCP/Ports]", "VMState"]

#vars needed for gevent (lock)
sem = BoundedSemaphore(1)

####functions needed for testbed manager threads:
def getVMInfo(session, machine):
	answer = {}
	answer ["name"] = str(machine.name)
	answer ["groups"] = machine.groups
	answer["vrde"] = machine.VRDEServer.enabled
	answer["vrdeproperty[TCP/Ports]"] = str(machine.VRDEServer.getVRDEProperty('TCP/Ports'))
	answer["VMState"] = machine.state
	
	#need active machine/console for the following:
	if session.state != mgr.constants.SessionState_Unlocked:
		print "session is locked, cannot get console"
		return answer
		
	machine.lockMachine(session, mgr.constants.LockType_Shared)
	console = session.console
	#if can't get console, this means that the vm is probably off
	if console != None:
		answer ["VRDEActiveConnection"] = console.VRDEServerInfo.active
		res = console.display.getScreenResolution(0)
		#try to set it to 16 bpp to reduce throughput requirements
		if res > 16:
			print "Sending hint to adjust resolution"
			console.display.setVideoModeHint(0, True, False, 0, 0, 0, 0, 16)
			res = console.display.getScreenResolution(0)
			print "after",res
		answer["VideoMode"] = res[2]
		
	session.unlockMachine()
	return answer

def powerdown_machine(session, machine):
	try:
		if session.state != mgr.constants.SessionState_Unlocked:
			print "session is locked, not powering down"
			return -1
		machine.lockMachine(session, mgr.constants.LockType_Shared)
		console = session.console
		#if can't get console, this means that the vm is probably off
		if console != None:
			print "POWERDOWN"
			progress = console.powerdown()
			progress.waitForCompletion(-1)
		session.unlockMachine()
	except Exception as e:
		print "error during powerdown",e

def restore_machine(session, machine):
	try:
		if session.state != mgr.constants.SessionState_Unlocked:
			print "session is locked, not restoring vm"
			return -1
		try:
			machine.lockMachine(session, mgr.constants.LockType_Shared)
			snap = machine.currentSnapshot
			#have to reference using session for some weird reason!
			print "RESTORE"
			progress = session.machine.restoreSnapshot(snap)
			progress.waitForCompletion(-1)
		except Exception as e:
			save = False
			print(mgr, e)
			traceback.print_exc()
			#exit()
		session.unlockMachine()
	except Exception as e:
		print "error during restore",e

def start_machine(session, machine):
	try:
		if session.state != mgr.constants.SessionState_Unlocked:
			print "session is locked, not starting vm"
			return -1
		print "LAUNCH"
		progress = machine.launchVMProcess(session, "headless", "")
		progress.waitForCompletion(-1)
		
		session.unlockMachine()
	except Exception as e:
		print "error during start",e

def makeAvailableToNotAvailable(vmNameList):
	#print "making notAvailable",vmNameList,"\n"
	
	for vmName in vmNameList:
		sem.wait()
		sem.acquire()
		availableState.remove(vmName)
		notAvailableState.append(vmName)
		sem.release()
		
def makeNotAvailableToRestoreState(vmNameList):
	#print "making notAvailableToRestore:",vmNameList,"\n"
	
	for vmName in vmNameList:
		sem.wait()
		sem.acquire()
		notAvailableState.remove(vmName)
		restoreState.append(vmName)
		sem.release()
	
def makeRestoreToAvailableState(): #will look at restore buffer and process any items that exist
	global vms
	global groupToVms
	restoreSubstates = {}
	while True:
		#print "making restoreToAvailable:",vmNameList,"\n"
		try:
			#Need to reload all vms that are in the group of the vm in the "restore" state
				#get each vm in restoreState list
			for vmToRestore in restoreState:
				#if this vm has a group
				print "vmToRestore",vmToRestore
				if vmToRestore in vms and "groups" in vms[vmToRestore]:
					#get all vms in group
					groupToRestore = str(vms[vmToRestore]["groups"][0])
					print "groupToRestore",groupToRestore
					#add each vm in group to restoreSubstate list (if haven't already)
					for vmInGroup in groupToVms[groupToRestore]:
						print "vmInGroup",vmInGroup
						if vmInGroup not in restoreSubstates:
							restoreSubstates[vmInGroup] = "pending"
			#Process next stage in restore
			
			print restoreSubstates
			vmsToRemoveFromQueue = []
			for substate in restoreSubstates:
				#TODO: might replace this with a call to a shell script for timing reasons
				#output = subprocess.call(["restartFromSnap.bat", vmNameToRestore])
				print "Processing state for:",substate,restoreSubstates[substate]
				sem.wait()
				sem.acquire()
				mach = vbox.findMachine(substate)
				vmState = getVMInfo(session, mach)["VMState"]
				sem.release()
				print "currState:",vmState
				
				if restoreSubstates[substate] == "pending" and vmState == mgr.constants.MachineState_Running:
					print "CALLING POWEROFF",substate,":",restoreSubstates[substate]
					powerdown_machine(session, mach)
					restoreSubstates[substate] = "poweroff_sent"
					
				elif restoreSubstates[substate] == "poweroff_sent" and vmState == mgr.constants.MachineState_PoweredOff or vmState == mgr.constants.MachineState_Aborted:
					print "CALLING RESTORE",substate,":",restoreSubstates[substate]
					restore_machine(session, mach)
					restoreSubstates[substate] = "restorecurrent_sent"
					
				elif restoreSubstates[substate] == "restorecurrent_sent" and vmState == mgr.constants.MachineState_Saved:
					print "CALLING STARTVM",substate,":",restoreSubstates[substate]
					start_machine(session, mach)
					restoreSubstates[substate] = "startvm_sent"
				elif restoreSubstates[substate] == "startvm_sent" and vmState == mgr.constants.MachineState_Running:
					restoreSubstates[substate] = "complete"
					sem.wait()
					sem.acquire()
					if substate in restoreState:
						#remove from restore so it can be added to available buffer once again
						restoreState.remove(substate)
					if substate in notAvailableState:
						notAvailableState.remove(substate)
					sem.release()
					vmsToRemoveFromQueue.append(substate)
			
			for rem in vmsToRemoveFromQueue:
				if rem in restoreSubstates:
					del restoreSubstates[rem]
			time.sleep(sleepTime)
		except Exception as x:
			print "RESTORE: An error occured:",x
			time.sleep(sleepTime)
			pass
		
def makeNewToAvailableState(vmNameList):
	#print "making available:",vmNameList,"\n"
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
			currvms = {}
			currGroupToVms = {}
			
			#first get all vms
			for mach in vbox.machines:
				#print "MACHINE STATE!!!!!!!",mach.name,mach.state
				currvms[str(mach.name)] = getVMInfo(session, mach)

			#for each vm get info and place in state list
			for vm in currvms:
				#print "VMInfo:",vm,currvms[vm]["groups"],"\n\n"
				#get group name and add this vm to a dictionary of that group:
				for group in currvms[vm]["groups"]:
					gname = str(group)
					#print "GROUP Name:",gname
					if gname != "/":
						if gname not in currGroupToVms:
							currGroupToVms[gname] = []
						currGroupToVms[gname].append(vm)
			
			#so we get all at once (may have to create a lock?)
			sem.wait()
			sem.acquire()
			###lock###
			vms = currvms
			groupToVms = currGroupToVms
			###unlock###
			sem.release()
			
			#print "VMS:",vms
			#print "GROUPS:",groupToVms
			########Assign each vm into a state list############
				
				#first look at any "not available" to see if they go into the "restore" state
			nasList = []
			for vmName in vms:
				if "VRDEActiveConnection" in vms[vmName]:
					if vms[vmName]["VRDEActiveConnection"] == 1 and vmName in availableState and vmName not in notAvailableState and vmName not in restoreState:
						nasList.append(vmName)
					elif vms[vmName]["VRDEActiveConnection"] == 0 and vmName in notAvailableState and vmName not in restoreState and vmName not in restoreState:
						restoreState.append(vmName)
			
			makeAvailableToNotAvailable(nasList)
#Note that the restore thread will move vms in restore buffer available after processing
				#add any newly available vms into the available buffer
			av = []
			for vmName in vms:
				if "vrde" in vms[vmName] and vms[vmName]["vrde"] == 1 and vms[vmName]["VMState"] == mgr.constants.MachineState_Running:
					#make available
					if vmName not in notAvailableState and vmName not in restoreState and vmName not in availableState:
						av.append(vmName)
			makeNewToAvailableState(av)
			
				#add available info to available vms
			sem.wait()
			sem.acquire()
			availableInfo = []
			for vmName in availableState:
				if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
					availableInfo.append((vms[vmName]["name"], vms[vmName]["vrdeproperty[TCP/Ports]"]))
			sem.release()
			availableInfo.sort(key=lambda tup: tup[0])
			
			#Print out status
			print "\n\n\n"
			print "status:"
			print "available:",availableState
			print "notAvailable:",notAvailableState
			print "restore:",restoreState
			
			time.sleep(sleepTime)
			
		except Exception as x:
			print "STATES: An error occured:",x
			
app = Flask(__name__)
app.debug = True

# Simple catch-all server
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    return render_template('show_data.html', templateAvailable=availableInfo)

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8080), app)
    srv_greenlet = gevent.spawn(http_server.start)
    
    stateAssignmentThread = gevent.spawn(manageStates)
    restoreThread = gevent.spawn(makeRestoreToAvailableState)
    
    stateAssignmentThread.start()   
    restoreThread.start()
    
    try:
        gevent.joinall([srv_greenlet, stateAssignmentThread, restoreThread])
    except KeyboardInterrupt:
        print "Exiting"
