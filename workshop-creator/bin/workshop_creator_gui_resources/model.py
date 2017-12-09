import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import threading
import re
import shutil
import zipfile
import workshop_creator_gui_resources.gui_constants as gui_constants
from workshop_creator_gui_resources.process_window import ProcessWindow
from lxml import etree

VBOXMANAGE_DIRECTORY = gui_constants.VBOXMANAGE_DIRECTORY
WORKSHOP_CONFIG_DIRECTORY = gui_constants.WORKSHOP_CONFIG_DIRECTORY
WORKSHOP_MATERIAL_DIRECTORY = gui_constants.WORKSHOP_MATERIAL_DIRECTORY
WORKSHOP_RDP_DIRECTORY = gui_constants.WORKSHOP_RDP_DIRECTORY
MANAGER_SAVE_DIRECTORY = gui_constants.MANAGER_SAVE_DIRECTORY

class Session:
    def __init__(self):
      self.workshopList = []
      self.currentWorkshop = None
      self.currentVM = None
      self.loadXMLFiles(WORKSHOP_CONFIG_DIRECTORY)

    def runWorkshop(self):
        if self.currentWorkshop != None:
            self.holdDirectory = MANAGER_SAVE_DIRECTORY+self.currentWorkshop.filename+"/"
            if not os.path.exists(self.holdDirectory):
                os.makedirs(self.holdDirectory)
            if not os.path.exists(self.holdDirectory+"Materials/"):
                os.makedirs(self.holdDirectory+"Materials/")
            if not os.path.exists(self.holdDirectory+"RDP/"):
                os.makedirs(self.holdDirectory+"RDP/")

            for holdFile in os.listdir(self.holdDirectory+"Materials/"):
                os.remove(self.holdDirectory+"Materials/"+holdFile)

            for holdFile in os.listdir(self.holdDirectory+"RDP/"):
                os.remove(self.holdDirectory+"RDP/"+holdFile)

            for material in self.currentWorkshop.materialList:
                shutil.copy2(WORKSHOP_MATERIAL_DIRECTORY+self.currentWorkshop.filename+"/"+material.name, self.holdDirectory+"/Materials/")

            for rdpfile in os.listdir(WORKSHOP_RDP_DIRECTORY+self.currentWorkshop.filename):
                shutil.copy2(WORKSHOP_RDP_DIRECTORY+self.currentWorkshop.filename+"/"+rdpfile, self.holdDirectory+"/RDP/")

    def runScript(self, script):
        if self.currentWorkshop != None:
            #t = threading.Thread(target=self.scriptWorker, args=[WORKSHOP_CONFIG_DIRECTORY+self.currentWorkshop.filename+".xml", script])
            self.scriptWorker(WORKSHOP_CONFIG_DIRECTORY+self.currentWorkshop.filename+".xml", script)
            #t.start()

    def scriptWorker(self, filePath, script):
        #subprocess.call(["python", script, filePath])
        #pw = ProcessWindow(["ping", "localhost", "-t"])
        pw = ProcessWindow(["python", script, filePath])
        #pw = ProcessWindow("python " + script + " " + filePath)


    # Thread function, performs unzipping operation
    def unzipWorker(self, zipPath, spinnerDialog):
        unzip = zipfile.ZipFile(zipPath, 'r')
        unzip.extractall(zipPath+"/../creatorImportTemp")
        unzip.close()
        spinnerDialog.destroy()

    def importUnzip(self, zipPath, spinnerDialog):
        t = threading.Thread(target=self.unzipWorker, args=[zipPath, spinnerDialog])
        t.start()

    def importToVBox(self, tempPath, spinnerDialog):
        t = threading.Thread(target=self.importWorker, args=[tempPath, spinnerDialog])
        t.start()

    def importWorker(self, tempPath, spinnerDialog):
        subprocess.call([VBOXMANAGE_DIRECTORY, "import", tempPath])
        spinnerDialog.destroy()

    # Thread function, performs zipping operaiton
    def zipWorker(self, folderPath, spinnerDialog):
        d = folderPath

        os.chdir(os.path.dirname(d))
        with zipfile.ZipFile(d + '.zip',
                             "w",
                             zipfile.ZIP_DEFLATED,
                             allowZip64=True) as zf:
            for root, _, filenames in os.walk(os.path.basename(d)):
                for name in filenames:
                    name = os.path.join(root, name)
                    name = os.path.normpath(name)
                    zf.write(name, name)

        spinnerDialog.destroy()
        shutil.rmtree(folderPath)
        #need to find a way to re-enable warning msg
        #WarningDialog(self, "Export completed.")

    def exportZipFiles(self, folderPath, spinnerDialog):
            shutil.copy2("workshop_creator_gui_resources/workshop_configs/"+self.currentWorkshop.filename+".xml", folderPath)
            t = threading.Thread(target=self.zipWorker, args=[folderPath, spinnerDialog])
            t.start()


    def getCurrentVMList(self):
        return self.currentWorkshop.vmList

    def exportWorkshop(self, folderPath, spinnerDialog):

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        if not os.path.exists(folderPath+"/Materials/"):
            os.makedirs(folderPath+"/Materials/")
        for material in self.currentWorkshop.materialList:
            shutil.copy2(WORKSHOP_MATERIAL_DIRECTORY+self.currentWorkshop.filename+"/"+material.name, folderPath+"/Materials")

        if not os.path.exists(folderPath+"/RDP/"):
            os.makedirs(folderPath+"/RDP/")
        if os.path.exists(WORKSHOP_RDP_DIRECTORY+self.currentWorkshop.filename):
            for rdpfile in os.listdir(WORKSHOP_RDP_DIRECTORY+self.currentWorkshop.filename):
                shutil.copy2(WORKSHOP_RDP_DIRECTORY+self.currentWorkshop.filename+"/"+rdpfile, folderPath+"/RDP/")

        for vm in self.currentWorkshop.vmList:
            subprocess.call([VBOXMANAGE_DIRECTORY, 'export', vm.name, '-o', folderPath+'/'+vm.name+'.ova'])


        self.exportZipFiles(folderPath, spinnerDialog)
        #spinnerDialog2.run()

    def getAvailableVMs(self):
        vmList = subprocess.check_output([VBOXMANAGE_DIRECTORY, "list", "vms"])
        vmList = re.findall("\"(.*)\"", vmList)

        matchFound = True
        for vm in self.currentWorkshop.vmList:
            thisMatchFound=False
            for registeredVM in vmList:
                if vm.name == registeredVM:
                    thisMatchFound = True
                    break
            if thisMatchFound == False:
                matchFound = False

        return matchFound

    def removeVM(self):

        self.currentWorkshop.vmList.remove(self.currentVM)

    def removeMaterial(self):
        self.holdDirectory = WORKSHOP_MATERIAL_DIRECTORY+self.currentWorkshop.filename+"/"
        if os.path.exists(self.holdDirectory+self.currentMaterial.name):
            os.remove(self.holdDirectory+self.currentMaterial.name)
        self.currentWorkshop.materialList.remove(self.currentMaterial)

    def removeWorkshop(self):

        os.remove(WORKSHOP_CONFIG_DIRECTORY+"/"+self.currentWorkshop.filename+".xml")
        self.workshopList.remove(self.currentWorkshop)

    def addWorkshop(self, workshopName, vmName):

        self.workshopList.append(Workshop(workshopName, vmName))

    def addVM(self, vmName):

        self.currentWorkshop.addVM(vmName)

    def addMaterial(self, materialAddress):
        self.holdName = os.path.basename(materialAddress)
        self.currentWorkshop.addMaterial(materialAddress, self.holdName)

        self.holdDirectory = WORKSHOP_MATERIAL_DIRECTORY+self.currentWorkshop.filename+"/"
        if not os.path.exists(self.holdDirectory):
            os.makedirs(self.holdDirectory)

        if not os.path.exists(self.holdDirectory+self.holdName):
            shutil.copy2(materialAddress, self.holdDirectory+self.holdName)

    # This will load xml files
    def loadXMLFiles(self, directory):

        # Here we will iterate through all the files that end with .xml
        #in the workshop_configs directory
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                workshop = Workshop(filename, None)
                workshop.loadFileConfig(filename)
                self.workshopList.append(workshop)

    def softSaveWorkshop(self, inPath, inIPAddress, inBaseGroupName, inCloneNumber, inCloneSnapshots, inLinkedClones, inBaseOutName, inVRDPBaseport):
        self.oldNumOfClones = self.currentWorkshop.numOfClones
        self.oldCloneSnapshots = self.currentWorkshop.cloneSnapshots
        self.oldLinkedClones = self.currentWorkshop.linkedClones
        self.oldBaseGroupName = self.currentWorkshop.baseGroupName
        self.oldBaseOutName = self.currentWorkshop.baseOutName
        self.oldVRDPBaseport = self.currentWorkshop.vrdpBaseport

        self.currentWorkshop.pathToVBoxManage = inPath
        self.currentWorkshop.ipAddress = inIPAddress
        self.currentWorkshop.baseGroupName = inBaseGroupName
        self.currentWorkshop.numOfClones = inCloneNumber
        self.currentWorkshop.cloneSnapshots = inCloneSnapshots
        self.currentWorkshop.linkedClones = inLinkedClones
        self.currentWorkshop.baseOutName = inBaseOutName
        self.currentWorkshop.vrdpBaseport = inVRDPBaseport

        if (self.oldNumOfClones != self.currentWorkshop.numOfClones) or (self.oldCloneSnapshots != self.currentWorkshop.cloneSnapshots) or (self.oldLinkedClones != self.currentWorkshop.linkedClones) or (self.oldBaseGroupName != self.currentWorkshop.baseGroupName) or (self.oldBaseOutName != self.currentWorkshop.baseOutName) or (self.oldVRDPBaseport != self.currentWorkshop.vrdpBaseport):
            self.hardSave()
            self.runRDPScript()

    def softSaveMaterial(self, inMaterialName):
        if self.currentMaterial.name != inMaterialName:
            os.rename(WORKSHOP_MATERIAL_DIRECTORY+self.currentWorkshop.filename+"/"+self.currentMaterial.name, WORKSHOP_MATERIAL_DIRECTORY+self.currentWorkshop.filename+"/"+inMaterialName)
            self.currentMaterial.name = inMaterialName

    def runRDPScript(self):
        for rdpfile in os.listdir(WORKSHOP_RDP_DIRECTORY+self.currentWorkshop.filename):
            os.remove(WORKSHOP_RDP_DIRECTORY+self.currentWorkshop.filename+"/"+rdpfile)
        self.runScript("workshop-rdp.py")

    def softSaveVM(self, inVMName, inVRDPEnabled, inInternalnetBasenameList):

        self.somethingChanged = ((self.currentVM.name != inVMName) or (self.currentVM.vrdpEnabled != inVRDPEnabled))
        if not self.somethingChanged:
            self.somethingChanged = (self.currentVM.internalnetBasenameList != inInternalnetBasenameList)

        if self.somethingChanged:
            self.currentVM.name = inVMName
            self.currentVM.vrdpEnabled = inVRDPEnabled
            #self.currentVM.internalnetBasenameList = inInternalnetBasenameList
            self.hardSave()
            self.runRDPScript()


    def hardSave(self):

        for workshop in self.workshopList:

            # Create root of XML etree
            root = etree.Element("xml")

            # Populate vbox-setup fields
            vbox_setup_element = etree.SubElement(root, "vbox-setup")
            etree.SubElement(vbox_setup_element, "path-to-vboxmanage").text = workshop.pathToVBoxManage

            # Populate testbed-setup fields
            testbed_setup_element = etree.SubElement(root, "testbed-setup")
            network_config_element = etree.SubElement(testbed_setup_element, "network-config")
            etree.SubElement(network_config_element, "ip-address").text = workshop.ipAddress

            # Populate vm-set fields
            vm_set_element = etree.SubElement(testbed_setup_element, "vm-set")
            etree.SubElement(vm_set_element, "base-groupname").text = workshop.baseGroupName
            etree.SubElement(vm_set_element, "num-clones").text = workshop.numOfClones
            etree.SubElement(vm_set_element, "clone-snapshots").text = workshop.cloneSnapshots
            etree.SubElement(vm_set_element, "linked-clones").text = workshop.linkedClones
            etree.SubElement(vm_set_element, "base-outname").text = workshop.baseOutName
            etree.SubElement(vm_set_element, "vrdp-baseport").text = workshop.vrdpBaseport

            # Iterate through list of VMs and whether vrdp is enabled for that vm
            for vm in workshop.vmList:
                vm_element = etree.SubElement(vm_set_element, "vm")
                etree.SubElement(vm_element, "name").text = vm.name
                etree.SubElement(vm_element, "vrdp-enabled").text = vm.vrdpEnabled
                for internalnet in vm.internalnetBasenameList:
                    etree.SubElement(vm_element, "internalnet-basename").text = internalnet

            self.holdDirectory = WORKSHOP_MATERIAL_DIRECTORY+workshop.filename+"/"
            if not os.path.exists(self.holdDirectory):
                os.makedirs(self.holdDirectory)

            for material in workshop.materialList:
                material_element = etree.SubElement(vm_set_element, "material")
                etree.SubElement(material_element, "name").text = material.name

            # Create tree for writing to XML file
            tree = etree.ElementTree(root)

            # Write tree to XML config file
            tree.write(WORKSHOP_CONFIG_DIRECTORY+workshop.filename+".xml", pretty_print = True)

class Material:
    def __init__(self, materialAddress, materialName):

        self.address = materialAddress
        self.name = materialName
        #self.name = self.address.split('\\')
        #self.name = self.name[len(self.name)-1]

class VM:

    def __init__(self, vmName):

        # These fields are VM specific
        self.name = vmName # String
        self.vrdpEnabled = "false" # Bool

        # This will contain a list of basenames
        self.internalnetBasenameList = [] # String
        self.internalnetBasenameList.append("intnet")

class Workshop:

    def __init__(self, workshopName, vmName):

        self.filename = workshopName

        # These fields are workshop specific
        self.pathToVBoxManage = VBOXMANAGE_DIRECTORY # String
        self.ipAddress = "127.0.0.1" # String
        self.baseGroupName = workshopName # String
        self.numOfClones = "1" # Int
        self.cloneSnapshots = "false" # Bool
        self.linkedClones = "false" # Bool
        self.baseOutName = "101" # String
        self.vrdpBaseport = "1011" # int


        self.vmList = [] # VM
        if vmName!=None:
          # This will contain a list of VM objects
          vm=VM(vmName)
          self.vmList.append(vm);

        self.materialList = []

    def addVM(self, vmName):

        self.vmList.append(VM(vmName))

    def addMaterial(self, materialAddress, materialName):
        self.materialList.append(Material(materialAddress, materialName))

    def loadFileConfig(self, inputFile):

        self.filename = os.path.splitext(inputFile)[0]

        tree = ET.parse(gui_constants.WORKSHOP_CONFIG_DIRECTORY+inputFile)
        root = tree.getroot()

        self.pathToVBoxManage = root.find('vbox-setup').find('path-to-vboxmanage').text.rstrip().lstrip()

        vmset = root.find('testbed-setup').find('network-config')
        self.ipAddress = vmset.find('ip-address').text.rstrip().lstrip()

        vmset = root.find('testbed-setup').find('vm-set')
        self.baseGroupName = vmset.find('base-groupname').text.rstrip().lstrip()
        self.numOfClones = vmset.find('num-clones').text.rstrip().lstrip()
        self.cloneSnapshots = vmset.find('clone-snapshots').text.rstrip().lstrip()
        self.linkedClones = vmset.find('linked-clones').text.rstrip().lstrip()
        self.baseOutName = vmset.find('base-outname').text.rstrip().lstrip()
        self.vrdpBaseport = vmset.find('vrdp-baseport').text.rstrip().lstrip()

        for vm in vmset.findall('vm'):
            currentVM = VM(vm.find('name').text.rstrip().lstrip())
            currentVM.vrdpEnabled = vm.find('vrdp-enabled').text.rstrip().lstrip()
            internalnetList = vm.findall('internalnet-basename')
            currentVM.internalnetBasenameList=[]
            for internalnet in internalnetList:
                currentVM.internalnetBasenameList.append(internalnet.text.rstrip().lstrip())
            self.vmList.append(currentVM)

        for material in vmset.findall('material'):
            currentMaterial = Material('', material.find('name').text.rstrip().lstrip())
            self.materialList.append(currentMaterial)
