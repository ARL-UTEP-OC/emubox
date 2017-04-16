import subprocess
import shutil
import xml.etree.ElementTree as ET
import shlex
import sys


def printError(message):
	print "\r\n\r\n!!!!!!!!!!\r\nERROR:\r\n",message,"\r\n!!!!!!!!!!\r\n"
	print "Exiting..."
	exit()			

if len(sys.argv) < 2:
	print "Usage: python workshop-creatory.py <input filename>"
	exit()
	
inputFilename = sys.argv[1]

tree = ET.parse(inputFilename)
root = tree.getroot()

pathToVirtualBox = root.find('vbox-setup').find('path-to-vboxmanage').text.rstrip().lstrip()
vmset = root.find('testbed-setup').find('vm-set')

#---here we look at each vmset
numClones = int(vmset.find('num-clones').text.rstrip().lstrip())
cloneSnapshots = vmset.find('clone-snapshots').text.rstrip().lstrip()
linkedClones = vmset.find('linked-clones').text.rstrip().lstrip()
baseGroupname = vmset.find('base-groupname').text.rstrip().lstrip()

netAdapter = vmset.find('internalnet-basename').text.rstrip().lstrip()

baseOutname=vmset.find('base-outname').text.rstrip().lstrip()

vrdpBaseport=vmset.find('vrdp-baseport').text.rstrip().lstrip()

for vm in vmset.findall('vm'):
	myBaseOutname = baseOutname	
	for i in range(1,numClones+1):
		vmname = vm.find('name').text.rstrip().lstrip()

		#check to make sure the vm exists:
		getVMsCmd = [pathToVirtualBox, "list", "vms"]
		vmList = subprocess.check_output(getVMsCmd)
		if vmname not in vmList:
			print "VM not found: ",vmname
			print "Exiting"
			exit()
			
		netAdapterName = netAdapter+myBaseOutname+str(i)
		
		#clone the vm and give it a name ending with myBaseOutname
		cloneCmd = [pathToVirtualBox, "clonevm", vmname, "--register"]
		if cloneSnapshots=='true':
			if linkedClones=='true':
				try:
					#get the name of the newest snapshot
					getSnapCmd = [pathToVirtualBox,"snapshot", vmname, "list","--machinereadable"]
					snapList = subprocess.check_output(getSnapCmd)
					latestSnapUUID = snapList.split("CurrentSnapshotUUID=\"")[1].split("\"")[0]
					cloneCmd.append("--snapshot")
					cloneCmd.append(latestSnapUUID)
					cloneCmd.append("--options")	
					cloneCmd.append("link")			
				except Exception:
					printError("Using the link clone option requires that VMs contain a snapshot. No snapshot found for vm:"+ vmname)
					print "Exiting..."
					exit()			
			else:
				cloneCmd.append("--mode")
				cloneCmd.append("all")
		newvmName = vmname+myBaseOutname+str(i)
		cloneCmd.append("--name")
		cloneCmd.append(newvmName)
		print("\nexecuting: ")
		print(cloneCmd)
		try:
			result = subprocess.check_output(cloneCmd)
		except Exception:
			printError("Make sure that the clone does not already exist:"+newvmName)
			exit()
		print("\nresult: ")
		print(result)
		
		#internal network setup
		intNetCmd = [pathToVirtualBox, "modifyvm", newvmName, "--nic1","intnet","--intnet1",netAdapterName]
		print("\nsetting up internal network adapter")
		print("executing: ")
		print(intNetCmd)
		result = subprocess.check_output(intNetCmd)
		#commented out the next line because an error about non-mutable state is reported even thought it still completes successfully
		#print(result)

		#for some reason, the vms aren't placed into a group unless we execute an additional modify command
		try:
			groupCmd = [pathToVirtualBox, "modifyvm", newvmName, "--groups", "/"+baseGroupname + "/"+netAdapterName]
			print("\nsetting up vrdp for " + newvmName)
			print("\nexecuting: ")
			print(groupCmd)
			result = subprocess.check_output(groupCmd)
			print(result)
		except Exception:
			print "Could not move VM",newvmName, "to group:",netAdapterName
					
		#vrdp setup
		vrdpEnabled = vm.find('vrdp-enabled').text.rstrip().lstrip()
		if vrdpEnabled and vrdpEnabled=='true':
			vrdpCmd = [pathToVirtualBox, "modifyvm", newvmName, "--vrde", "on", "--vrdeport", str(vrdpBaseport)]
			print("\nsetting up vrdp for " + newvmName)
			print("\nexecuting: ")
			print(vrdpCmd)
			result = subprocess.check_output(vrdpCmd)
			print(result)
			vrdpBaseport = str(int(vrdpBaseport)+1)
		#finally create a snapshot after the vm is setup
		try:
			snapCmd = [pathToVirtualBox, "snapshot", newvmName, "take", "ready"]
			print("\ntaking snapshot for " + newvmName)
			print("\nexecuting: ")
			print(snapCmd)
			result = subprocess.check_output(snapCmd)
			print(result)
		except Exception:
			print "Could take snapshot for VM",newvmName
