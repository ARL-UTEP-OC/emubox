import xml.etree.ElementTree as ET
import sys

inputFilename = sys.argv[1]

tree = ET.parse(inputFilename)
root = tree.getroot()

pathToVirtualBox = root.find('vbox-setup').find('path-to-vboxmanage').text.rstrip().lstrip()
vmset = root.find('testbed-setup').find('vm-set')

numClones = int(vmset.find('num-clones').text.rstrip().lstrip())
cloneSnapshots = vmset.find('clone-snapshots').text.rstrip().lstrip()
linkedClones = vmset.find('linked-clones').text.rstrip().lstrip()
baseGroupname = vmset.find('base-groupname').text.rstrip().lstrip()

baseOutname = vmset.find('base-outname').text.rstrip().lstrip()

vrdpBaseport = vmset.find('vrdp-baseport').text.rstrip().lstrip()

VM_LIST = []
for vm in vmset.findall('vm'):
	curr_vm = []
	curr_vm.append(vm.find('name').text.rstrip().lstrip())
	curr_vm.append(vm.find('vrdp-enabled').text.rstrip().lstrip())
	internalnets = vm.findall('internalnet-basename')
	internalnetNames = []
	for internalnet in internalnets:
		internalnetNames.append(internalnet.text.rstrip().lstrip())
	curr_vm.append(internalnetNames)
	VM_LIST.append(curr_vm)

	# For testing
print [numClones, cloneSnapshots, linkedClones, baseGroupname, baseOutname, vrdpBaseport]
print VM_LIST
