import os
import subprocess
import re
import xml.etree.ElementTree as ET
from src.gui_constants import VBOXMANAGE_DIRECTORY, WORKSHOP_CONFIG_DIRECTORY


def getVMs():
    getVMsCmd = [VBOXMANAGE_DIRECTORY, "list", "vms"]
    vmList = subprocess.check_output(getVMsCmd)
    vmList = re.findall("\"(.*)\"", vmList)
    return list(vmList)


def getCloneNames(workshopName):
    names = []
    inputFilename = os.path.join(WORKSHOP_CONFIG_DIRECTORY, workshopName + ".xml")
    tree = ET.parse(inputFilename)
    root = tree.getroot()

    vmset = root.find('testbed-setup').find('vm-set')
    numClones = int(vmset.find('num-clones').text)
    baseOutname = vmset.find('base-outname').text

    for vm in vmset.findall('vm'):
        myBaseOutname = baseOutname
        for i in range(1, numClones + 1):
            vmname = vm.find('name').text
            newvmName = vmname + myBaseOutname + str(i)
            names.append(newvmName)
    return list(names)


def isRunning(workshopName):
    clone_names = getCloneNames(workshopName)
    for clone_name in clone_names:
        cmd = VBOXMANAGE_DIRECTORY + \
              " showvminfo " + "\"" + clone_name + "\" | grep -c \"running (since\""
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        output = int(output)
        if output == 0:
            return False
    return True


def hasClonesCreated(workshopName):
    vms = getVMs()
    clone_names = getCloneNames(workshopName)
    return set(clone_names) <= set(vms)


def getStatus(workshopName):
    # Check if clones are created
    if not hasClonesCreated(workshopName):
        return "Clones Not Created"
    # Clones are created. Check if running
    if isRunning(workshopName):
        return "Running"
    # Workshop is not running
    return "Ready"
