import subprocess
import shutil
import xml.etree.ElementTree as ET
import shlex
import sys

def printError(message):
    print "\r\n\r\n!!!!!!!!!!\r\nERROR:\r\n", message, "\r\n!!!!!!!!!!\r\n"
    print "Exiting..."
    exit()

if len(sys.argv) < 2:
    print "Usage: python workshop-restore.py <input filename>"
    exit()

inputFilename = sys.argv[1]

tree = ET.parse(inputFilename)
root = tree.getroot()

pathToVirtualBox = root.find('vbox-setup').find('path-to-vboxmanage').text.rstrip().lstrip()
vmset = root.find('testbed-setup').find('vm-set')

# ---here we look at each vmset
numClones = int(vmset.find('num-clones').text.rstrip().lstrip())
cloneSnapshots = vmset.find('clone-snapshots').text.rstrip().lstrip()
linkedClones = vmset.find('linked-clones').text.rstrip().lstrip()
baseGroupname = vmset.find('base-groupname').text.rstrip().lstrip()

baseOutname = vmset.find('base-outname').text.rstrip().lstrip()

vrdpBaseport = vmset.find('vrdp-baseport').text.rstrip().lstrip()

for vm in vmset.findall('vm'):
    myBaseOutname = baseOutname
    for i in range(1, numClones + 1):
        vmname = vm.find('name').text.rstrip().lstrip()
        newvmName = vmname + myBaseOutname + str(i)

        # check to make sure the vm exists:
        getVMsCmd = [pathToVirtualBox, "list", "vms"]
        vmList = subprocess.check_output(getVMsCmd)

        if newvmName  not in vmList:
            print "VM not found: ", newvmName
            continue

        try:
            restoreSnapCmd = [pathToVirtualBox, "snapshot", newvmName, "restorecurrent"]
            print("\nRestoring snapshot for " + newvmName)
            print("\nexecuting: ")
            print(restoreSnapCmd)
            result = subprocess.check_output(restoreSnapCmd)
            print(result)
        except Exception:
            print "Could not restore snapshot for VM", newvmName
