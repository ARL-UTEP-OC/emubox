import os
import subprocess
import threading
import re
import shutil
import zipfile
import logging
from lxml import etree
from src.gui.dialogs.process_dialog import ProcessDialog
from src.model.Workshop import Workshop
from src.gui_constants import (MANAGER_SAVE_DIRECTORY, WORKSHOP_CONFIG_DIRECTORY,
                               WORKSHOP_MATERIAL_DIRECTORY, WORKSHOP_RDP_CREATOR_FILE_PATH,
                               WORKSHOP_RDP_DIRECTORY, VBOXMANAGE_DIRECTORY)


class Session:

    def __init__(self):
        logging.debug("Creating Session")
        self.workshopList = []
        self.currentWorkshop = None
        self.currentVM = None
        self.loadXMLFiles(WORKSHOP_CONFIG_DIRECTORY)

    def overwriteRDPToManagerSaveDirectory(self):
        logging.debug("overwriteRDPToManagerSaveDirectory() initiated")
        rdpSourceDir = os.path.join(WORKSHOP_RDP_DIRECTORY, self.currentWorkshop.baseGroupName)
        if self.currentWorkshop is not None:
            self.holdDirectory = os.path.join(MANAGER_SAVE_DIRECTORY, self.currentWorkshop.baseGroupName)
            if not os.path.exists(self.holdDirectory):
                os.makedirs(self.holdDirectory)
            rdpPath = os.path.join(self.holdDirectory, "RDP")
            if os.path.exists(rdpPath):
                shutil.rmtree(rdpPath, ignore_errors=True)
            os.makedirs(rdpPath)

            for holdFile in os.listdir(rdpPath):
                os.remove(os.path.join(rdpPath, holdFile))

            logging.debug("Starting copy, taking files from: " + rdpSourceDir + " -- " + str(os.listdir(rdpSourceDir)))

            for rdpfile in os.listdir(rdpSourceDir):
                logging.debug(
                    "executing copy: " + os.path.join(rdpSourceDir, rdpfile) + " to " + os.path.join(self.holdDirectory,
                                                                                                     "RDP"))
                shutil.copy2(os.path.join(rdpSourceDir, rdpfile),
                             os.path.join(self.holdDirectory, "RDP"))

    def overwriteMaterialsToManagerSaveDirectory(self):
        # TODO; may optimize by only deleting the single file in the manager directory
        logging.debug("overwriteMaterialsToManagerSaveDirectory() initiated")
        materialsSourceDir = os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.baseGroupName)
        if self.currentWorkshop is not None:
            self.holdDirectory = os.path.join(MANAGER_SAVE_DIRECTORY, self.currentWorkshop.baseGroupName)
            if not os.path.exists(self.holdDirectory):
                os.makedirs(self.holdDirectory)
            materialsPath = os.path.join(self.holdDirectory, "Materials")
            if os.path.exists(materialsPath):
                shutil.rmtree(materialsPath, ignore_errors=True)
            os.makedirs(materialsPath)

            for holdFile in os.listdir(materialsPath):
                os.remove(os.path.join(materialsPath, holdFile))

            logging.debug("Starting copy, taking files from: " + materialsSourceDir + " -- " + str(os.listdir(materialsSourceDir)))

            for materialsFile in os.listdir(materialsSourceDir):
                logging.debug("executing copy: " + os.path.join(materialsSourceDir, materialsFile) + " to " + os.path.join(self.holdDirectory,"Materials"))
                shutil.copy2(os.path.join(materialsSourceDir, materialsFile),
                os.path.join(self.holdDirectory, "Materials"))

    def overwriteAllToSaveDirectory(self):
        # separate the below into 2 functions (materials, rdp); then call both
        logging.debug("overwriteAllToSaveDirectory() initiated")

        self.overwriteRDPToManagerSaveDirectory()
        self.overwriteMaterialsToManagerSaveDirectory()

    def runScript(self, script):
        logging.debug("runScript() initiated " + str(script))
        if self.currentWorkshop != None:
            self.scriptWorker(os.path.join(WORKSHOP_CONFIG_DIRECTORY, self.currentWorkshop.filename + ".xml"), script)

    def scriptWorker(self, filePath, script):
        logging.debug("scriptWorker() initiated " + str(filePath) + " " + script)
        pd = ProcessDialog("python -u \"" + script + "\" \"" + filePath + "\"")
        pd.set_title("Processing... please wait")
        pd.run()
        pd.destroy()

    # Thread function, performs unzipping operation
    def unzipWorker(self, zipPath, spinnerDialog):
        logging.debug("unzipWorker() initiated " + str(zipPath))
        spinnerDialog.setTitleVal("Decompressing EBX archive")

        block_size = 1048576
        z = zipfile.ZipFile(zipPath, 'r')
        outputPath = os.path.join(os.path.dirname(zipPath), "creatorImportTemp")
        members_list = z.namelist()

        currmem_num = 0
        for entry_name in members_list:
            logging.debug("unzipWorker(): unzipping " + str(entry_name))
            # increment our file progress counter
            currmem_num = currmem_num + 1

            entry_info = z.getinfo(entry_name)
            i = z.open(entry_name)
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)

            filename = os.path.join(outputPath, entry_name)
            file_dirname = os.path.dirname(filename)
            if not os.path.exists(file_dirname):
                os.makedirs(file_dirname)

            o = open(filename, 'wb')
            offset = 0
            int_val = 0
            while True:
                b = i.read(block_size)
                offset += len(b)
                status = float(offset) / float(entry_info.file_size) * 100.
                if int(status) > int_val:
                    int_val = int(status)
                    spinnerDialog.setProgressVal(float(int_val / 100.))
                    spinnerDialog.setLabelVal("Processing file " + str(currmem_num) + "/" + str(
                        len(members_list)) + ":\r\n" + entry_name + "\r\nExtracting: " + str(int_val) + " %")
                if b == '':
                    break
                o.write(b)
        i.close()
        o.close()
        spinnerDialog.hide()

    def importUnzip(self, zipPath, spinnerDialog):
        logging.debug("importUnzip() initiated " + str(zipPath))
        t = threading.Thread(target=self.unzipWorker, args=[zipPath, spinnerDialog])
        t.start()

    def importToVBox(self, tempPath, spinnerDialog):
        logging.debug("importToVBox() initiated " + str(tempPath))
        t = threading.Thread(target=self.importVBoxWorker, args=[tempPath, spinnerDialog])
        t.start()

    def importVBoxWorker(self, tempPath, spinnerDialog):
        logging.debug("importVBoxWorker() initiated " + str(tempPath))
        spinnerDialog.setTitleVal("Importing into VirtualBox")
        subprocess.Popen([VBOXMANAGE_DIRECTORY, "import", tempPath]).communicate()
        spinnerDialog.hide()

    def exportFromVBox(self, tempPath, vmname, spinnerDialog):
        logging.debug("exportFromVBox() initiated " + str(tempPath))
        t = threading.Thread(target=self.exportVBoxWorker, args=[tempPath, vmname, spinnerDialog])
        t.start()

    def exportVBoxWorker(self, tempPath, vmname, spinnerDialog):
        logging.debug("exportVBoxWorker() initiated " + str(tempPath))
        spinnerDialog.setTitleVal("Exporting from VirtualBox")
        subprocess.Popen([VBOXMANAGE_DIRECTORY, "export", vmname, "-o", tempPath]).communicate()
        # spinnerDialog.destroy()

    def zipWorker(self, folderPath, spinnerDialog):
        logging.debug("zipWorker() initiated " + str(folderPath))

        d = folderPath

        os.chdir(os.path.dirname(d))
        contentToZip = os.walk(os.path.basename(d))
        numFiles = sum([len(files) for r, dirs, files in contentToZip])
        currFile = 0
        logging.debug("zipWorker(): Number files:" + str(numFiles))
        with zipfile.ZipFile(d + '.ebx',
                             "w",
                             zipfile.ZIP_DEFLATED,
                             allowZip64=True) as zf:
            for root, _, filenames in os.walk(os.path.basename(d)):
                logging.debug("zipWorker(): listing filenames " + str(filenames))
                for name in filenames:
                    logging.debug("zipWorker(): adding file: " + name)
                    currFile = currFile + 1
                    name = os.path.join(root, name)
                    name = os.path.normpath(name)
                    status = float(currFile / (numFiles * 1.))
                    logging.debug("adjusting dialog progress: " + str(status))
                    spinnerDialog.setLabelVal(
                        "Compressing to EBX archive " + str(currFile) + "/" + str(numFiles) + ": " + name)
                    spinnerDialog.setProgressVal(status)
                    zf.write(name, name)
        spinnerDialog.setLabelVal("--------Almost finished, cleaning temporary directories--------")
        spinnerDialog.setProgressVal(1)
        shutil.rmtree(folderPath, ignore_errors=True)
        # spinnerDialog.setLabelVal("--------Complete--------")
        spinnerDialog.hide()

    def exportZipFiles(self, folderPath, spinnerDialog):
        logging.debug("exportZipFiles() initiated " + str(folderPath))
        spinnerDialog.set_title("Zipping content...")
        shutil.copy2(os.path.join(WORKSHOP_CONFIG_DIRECTORY, self.currentWorkshop.filename + ".xml"), folderPath)
        t = threading.Thread(target=self.zipWorker, args=[folderPath, spinnerDialog])
        t.start()

    def getCurrentVMList(self):
        logging.debug("getCurrentVMList() initiated")
        return self.currentWorkshop.vmList

    def exportWorkshop(self, folderPath, spinnerDialog):
        logging.debug("exportWorkshop() initiated " + str(folderPath))
        # TODO: need to show a dialog warning users; but need to workout the spinnerDialog race condition first (hide before run)
        # Remove the folder if it exists
        if os.path.exists(folderPath):
            shutil.rmtree(folderPath)
        os.makedirs(folderPath)
        materialsPath = os.path.join(folderPath, "Materials")
        if os.path.exists(materialsPath):
            logging.error("Folder " + folderPath + " already exists. Cancelling export.")
            return
        os.makedirs(materialsPath)

        for material in self.currentWorkshop.materialList:
            shutil.copy2(os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.baseGroupName, material.name),
                         materialsPath)

        rdpPath = os.path.join(folderPath, "RDP")
        if os.path.exists(rdpPath):
            logging.error("Folder " + folderPath + " already exists. Cancelling export.")
            return
        os.makedirs(rdpPath)
        rdpFiles = os.path.join(WORKSHOP_RDP_DIRECTORY, self.currentWorkshop.baseGroupName)
        if os.path.exists(rdpFiles):
            for rdpfile in os.listdir(rdpFiles):
                shutil.copy2(os.path.join(rdpFiles, rdpfile), rdpPath)
        else:
            logging.debug("No RDP file found in path during export: " + str(rdpFiles))
        vmsToExport = self.currentWorkshop.vmList
        currVMNum = 0
        numVMs = len(vmsToExport)
        for vm in vmsToExport:
            # subprocess.call([VBOXMANAGE_DIRECTORY, 'export', vm.name, '-o', os.path.join(folderPath,vm.name+'.ova')])
            logging.debug("exportWorkshop(): Exporting VMS loop")
            logging.debug("Current VM NAME: " + vm.name)
            outputOva = os.path.join(folderPath, vm.name + '.ova')
            logging.debug("exportWorkshop(): adjusting dialog progress value to " + str(currVMNum / (numVMs * 1.)))
            spinnerDialog.setProgressVal(currVMNum / (numVMs * 1.))
            spinnerDialog.setLabelVal("Exporting VM " + str(currVMNum + 1) + "/" + str(numVMs) + ": " + str(vm.name))
            currVMNum = currVMNum + 1
            logging.debug("Checking if " + folderPath + " exists: ")
            if os.path.exists(folderPath):
                pd = ProcessDialog(VBOXMANAGE_DIRECTORY + " export \"" + vm.name + "\" -o \"" + outputOva + "\"")
                pd.run()
                pd.destroy()
            else:
                logging.error("folderPath" + folderPath + " was not created!")

        logging.debug("Done executing process. \r\nCreating zip")
        self.exportZipFiles(folderPath, spinnerDialog)

    def getAvailableVMs(self):
        logging.debug("getAvailableVMs() initiated")
        vmList = subprocess.check_output([VBOXMANAGE_DIRECTORY, "list", "vms"])
        vmList = re.findall("\"(.*)\"", vmList)

        matchFound = True
        for vm in self.currentWorkshop.vmList:
            thisMatchFound = False
            for registeredVM in vmList:
                logging.debug("getAvailableVMs(): checking if |" + vm.name + "| == |"  + registeredVM + "|")
                if vm.name == registeredVM:
                    thisMatchFound = True
                    break
            if thisMatchFound == False:
                matchFound = False
        return matchFound

    def removeVM(self):
        logging.debug("removeVM() initiated")
        self.currentWorkshop.vmList.remove(self.currentVM)

    def removeMaterial(self):
        logging.debug("removeMaterial() initiated")
        self.holdDirectory = os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.baseGroupName)
        materialFile = os.path.join(self.holdDirectory, self.currentMaterial.name)
        logging.debug("removeMaterial(): removing file: " + materialFile)
        if os.path.exists(materialFile):
            os.remove(materialFile)
        self.currentWorkshop.materialList.remove(self.currentMaterial)
        self.overwriteMaterialsToManagerSaveDirectory()

    def removeWorkshop(self):
        logging.debug("removeWorkshop() initiated ")
        # remove XML config file
        os.remove(os.path.join(WORKSHOP_CONFIG_DIRECTORY, self.currentWorkshop.filename + ".xml"))
        # remove materials associated with this workshop
        materialPath = os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.baseGroupName)
        if os.path.exists(materialPath):
            shutil.rmtree(materialPath, ignore_errors=True)
        # remove rdp files associated with this workshop
        rdpPath = os.path.join(WORKSHOP_RDP_DIRECTORY, self.currentWorkshop.baseGroupName)
        if os.path.exists(rdpPath):
            shutil.rmtree(rdpPath, ignore_errors=True)
        self.workshopList.remove(self.currentWorkshop)

    def addWorkshop(self, workshopName, vmName):
        logging.debug("addWorkshop() initiated")
        self.workshopList.append(Workshop(workshopName, vmName))

    def addVM(self, vmName):
        logging.debug("addVM() initiated " + str(vmName))
        self.currentWorkshop.addVM(vmName)

    def addMaterial(self, materialAddress):
        logging.debug("addMaterial() initiated " + str(materialAddress))
        self.holdName = os.path.basename(materialAddress)
        self.currentWorkshop.addMaterial(materialAddress, self.holdName)

        self.holdDirectory = os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.baseGroupName)
        if not os.path.exists(self.holdDirectory):
            os.makedirs(self.holdDirectory)

        if not os.path.exists(os.path.join(self.holdDirectory, self.holdName)):
            shutil.copy2(materialAddress, os.path.join(self.holdDirectory, self.holdName))
        # should copy all materials to manager director in addition to workshop-creator temp directory
        self.overwriteMaterialsToManagerSaveDirectory()

    # This will load xml files
    def loadXMLFiles(self, directory):
        logging.debug("loadXMLFiles() initiated " + str(directory))
        # Here we will iterate through all the files that end with .xml
        # in the workshop_configs directory
        if not os.path.exists(directory):
            os.makedirs(directory)
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                workshop = Workshop(filename, None)
                workshop.loadFileConfig(filename)
                self.workshopList.append(workshop)

    def softSaveWorkshop(self, inPath, inIPAddress, inBaseGroupName, inCloneNumber, inCloneSnapshots, inLinkedClones,
                         inBaseOutName, inVRDPBaseport):
        logging.debug("softSaveWorkshop() initiated")
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

        if (self.oldNumOfClones != self.currentWorkshop.numOfClones) or (
                self.oldCloneSnapshots != self.currentWorkshop.cloneSnapshots) or (
                self.oldLinkedClones != self.currentWorkshop.linkedClones) or (
                self.oldBaseGroupName != self.currentWorkshop.baseGroupName) or (
                self.oldBaseOutName != self.currentWorkshop.baseOutName) or (
                self.oldVRDPBaseport != self.currentWorkshop.vrdpBaseport):
            self.hardSave()
            self.runRDPScript()

    def softSaveMaterial(self, inMaterialName):
        logging.debug("softSaveMaterial() initiated " + str(inMaterialName))
        if self.currentMaterial.name != inMaterialName:
            os.rename(os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.baseGroupName,
                                   self.currentMaterial.name),
                      os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.filename, inMaterialName))
            self.currentMaterial.name = inMaterialName

    def runRDPScript(self):
        logging.debug("runRDPScript() initiated ")
        # this will generate the rdps and place them in the workshop-creator's folder
        currWorkshopFilename = os.path.join(WORKSHOP_RDP_DIRECTORY, self.currentWorkshop.baseGroupName)
        if os.path.exists(currWorkshopFilename):
            for rdpfile in os.listdir(currWorkshopFilename):
                os.remove(os.path.join(currWorkshopFilename, rdpfile))
        self.runScript(WORKSHOP_RDP_CREATOR_FILE_PATH)
        # this will copy the newly created rdp files to the manager folder
        self.overwriteRDPToManagerSaveDirectory()

    def softSaveVM(self, inVMName, inVRDPEnabled, inInternalnetBasenameList):
        logging.debug("softSaveVM() initiated ")
        self.somethingChanged = ((self.currentVM.name != inVMName) or (self.currentVM.vrdpEnabled != inVRDPEnabled))
        if not self.somethingChanged:
            self.somethingChanged = (self.currentVM.internalnetBasenameList != inInternalnetBasenameList)

        if self.somethingChanged:
            self.currentVM.name = inVMName
            self.currentVM.vrdpEnabled = inVRDPEnabled
            self.currentVM.internalnetBasenameList = inInternalnetBasenameList
            self.hardSave()
            self.runRDPScript()

    def hardSave(self):
        logging.debug("hardSave() initiated")
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
                logging.debug("hardSave(): iterating through VMs: |" + vm.name+"|")
                vm_element = etree.SubElement(vm_set_element, "vm")
                etree.SubElement(vm_element, "name").text = vm.name
                etree.SubElement(vm_element, "vrdp-enabled").text = vm.vrdpEnabled
                for internalnet in vm.internalnetBasenameList:
                    logging.debug("hardSave(): adding internalnet-basename: " + internalnet)
                    etree.SubElement(vm_element, "internalnet-basename").text = internalnet

            self.holdDirectory = os.path.join(WORKSHOP_MATERIAL_DIRECTORY, workshop.baseGroupName)
            if not os.path.exists(self.holdDirectory):
                os.makedirs(self.holdDirectory)

            for material in workshop.materialList:
                material_element = etree.SubElement(vm_set_element, "material")
                etree.SubElement(material_element, "name").text = material.name

            self.holdDirectory = os.path.join(WORKSHOP_RDP_DIRECTORY, workshop.baseGroupName)
            if not os.path.exists(self.holdDirectory):
                os.makedirs(self.holdDirectory)

            # Create tree for writing to XML file
            tree = etree.ElementTree(root)

            # Write tree to XML config file
            tree.write(os.path.join(WORKSHOP_CONFIG_DIRECTORY, workshop.filename + ".xml"), pretty_print=True)
