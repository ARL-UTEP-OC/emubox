import sys
import os
import xml.etree.ElementTree as ET

class VM:

    def __init__(self):

        # These fields are VM specific
        self.name = None # String
        self.vrdpEnabled = None # Bool

        # This will contain a list of basenames
        self.internalnetBasenameList = [] # String

class Workshop:

    def __init__(self):

        self.filename = None

        # These fields are workshop specific
        self.pathToVBoxManage = None # String
        self.ipAddress = None # String
        self.baseGroupName = None # String
        self.numOfClones = None # Int
        self.cloneSnapshots = None # Bool
        self.linkedClones = None # Bool
        self.baseOutName = None # String
        self.vrdpBaseport = None # int

        # This will contain a list of VM objects
        self.vmList = [] # VM

    def loadFileConfig(self, inputFile):

        self.filename = os.path.splitext(inputFile)[0]

        tree = ET.parse(os.getcwd()+"\\workshop_configs\\"+inputFile)
        root = tree.getroot()

        self.pathToVBoxManage = root.find('vbox-setup').find('path-to-vboxmanage').text.rstrip().lstrip()

        vmset = root.find('testbed-setup').find('network-config')
        self.ipAddress = vmset.find('ip-address').text.rstrip().lstrip()

        vmset = root.find('testbed-setup').find('vm-set')
        self.baseGroupName = vmset.find('base-groupname').text.rstrip().lstrip()
        self.numOfClones = int(vmset.find('num-clones').text.rstrip().lstrip())
        self.cloneSnapshots = vmset.find('clone-snapshots').text.rstrip().lstrip()
        self.linkedClones = vmset.find('linked-clones').text.rstrip().lstrip()
        self.baseOutname = vmset.find('base-outname').text.rstrip().lstrip()
        self.vrdpBaseport = vmset.find('vrdp-baseport').text.rstrip().lstrip()

        for vm in vmset.findall('vm'):
        	currentVM = VM()
        	currentVM.name = vm.find('name').text.rstrip().lstrip()
        	currentVM.vrdpEnabled = vm.find('vrdp-enabled').text.rstrip().lstrip()
        	internalnetList = vm.findall('internalnet-basename')

        	for internalnet in internalnetList:
        		currentVM.internalnetBasenameList.append(internalnet.text.rstrip().lstrip())

        self.vmList.append(currentVM)
