import os
import sys
import subprocess
import re
import threading
import shutil
import zipfile
import datetime

from lxml import etree

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from workshop_creator_gui_resources.gui_loader import Workshop
from workshop_creator_gui_resources.gui_loader import VM
from workshop_creator_gui_resources.gui_utilities import EntryDialog
from workshop_creator_gui_resources.gui_utilities import ListEntryDialog
from workshop_creator_gui_resources.gui_utilities import LoggingDialog
from workshop_creator_gui_resources.gui_utilities import ExportImportProgressDialog
from workshop_creator_gui_resources.gui_utilities import SpinnerDialog

import workshop_creator_gui_resources.gui_utilities as gui_utilities
import workshop_creator_gui_resources.gui_constants as gui_constants

# Constants
BOX_SPACING = gui_constants.BOX_SPACING
PADDING = gui_constants.PADDING
WORKSHOP_CONFIG_DIRECTORY = gui_constants.WORKSHOP_CONFIG_DIRECTORY
GUI_MENU_DESCRIPTION_DIRECTORY = gui_constants.GUI_MENU_DESCRIPTION_DIRECTORY
VBOXMANAGE_DIRECTORY = gui_constants.VBOXMANAGE_DIRECTORY
WORKSHOP_CREATOR_DIRECTORY = gui_constants.WORKSHOP_CREATOR_DIRECTORY


# This class is a container that contains the base GUI
class BaseWidget(Gtk.Box):

    def __init__(self):
        super(BaseWidget, self).__init__()

        self.set_border_width(PADDING)

        # Declaration of boxes
        self.outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.buttonsHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.vBoxManageHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.ipAddressHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.baseGroupNameHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.numClonesHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.cloneSnapshotsHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.linkedClonesHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.baseOutnameHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.vrdpBaseportHorBox = Gtk.Box(spacing=BOX_SPACING)

        # Declaration of labels
        self.vBoxManageLabel = Gtk.Label("Path To VBoxManager:")
        self.ipAddressLabel = Gtk.Label("IP Address:")
        self.baseGroupNameLabel = Gtk.Label("Base Group Name:")
        self.numClonesLabel = Gtk.Label("Number of Clones:")
        self.cloneSnapshotsLabel = Gtk.Label("Clone Snapshots:")
        self.linkedClonesLabel = Gtk.Label("Linked Clones:")
        self.baseOutnameLabel = Gtk.Label("Base Outname:")
        self.vrdpBaseportLabel = Gtk.Label("VRDP Baseport:")

        # Declaration of entrys
        self.vBoxManageEntry = Gtk.Entry()
        self.ipAddressEntry = Gtk.Entry()
        self.baseGroupNameEntry = Gtk.Entry()
        self.numClonesEntry = Gtk.Entry()
        self.cloneSnapshotsEntry = Gtk.Entry()
        self.linkedClonesEntry = Gtk.Entry()
        self.baseOutnameEntry = Gtk.Entry()
        self.vrdpBaseportEntry = Gtk.Entry()

        self.chooseVBoxPathButton = Gtk.Button("...")

        self.initializeContainers()
        self.initializeLabels()
        self.initializeEntrys()

        self.vBoxManageHorBox.pack_end(self.chooseVBoxPathButton, False, False, 0)


    def initializeContainers(self):
        self.add(self.outerVertBox)
        self.outerVertBox.add(self.buttonsHorBox)
        self.outerVertBox.add(self.vBoxManageHorBox)
        self.outerVertBox.add(self.ipAddressHorBox)
        self.outerVertBox.add(self.baseGroupNameHorBox)
        self.outerVertBox.add(self.numClonesHorBox)
        self.outerVertBox.add(self.cloneSnapshotsHorBox)
        self.outerVertBox.add(self.linkedClonesHorBox)
        self.outerVertBox.add(self.baseOutnameHorBox)
        self.outerVertBox.add(self.vrdpBaseportHorBox)

    def initializeLabels(self):
        self.vBoxManageHorBox.pack_start(self.vBoxManageLabel, False, False, PADDING)
        self.ipAddressHorBox.pack_start(self.ipAddressLabel, False, False, PADDING)
        self.baseGroupNameHorBox.pack_start(self.baseGroupNameLabel, False, False, PADDING)
        self.numClonesHorBox.pack_start(self.numClonesLabel, False, False, PADDING)
        self.cloneSnapshotsHorBox.pack_start(self.cloneSnapshotsLabel, False, False, PADDING)
        self.linkedClonesHorBox.pack_start(self.linkedClonesLabel, False, False, PADDING)
        self.baseOutnameHorBox.pack_start(self.baseOutnameLabel, False, False, PADDING)
        self.vrdpBaseportHorBox.pack_start(self.vrdpBaseportLabel, False, False, PADDING)

    def initializeEntrys(self):
        self.vBoxManageHorBox.pack_end(self.vBoxManageEntry, False, False, PADDING)
        self.ipAddressHorBox.pack_end(self.ipAddressEntry, False, False, PADDING)
        self.baseGroupNameHorBox.pack_end(self.baseGroupNameEntry, False, False, PADDING)
        self.numClonesHorBox.pack_end(self.numClonesEntry, False, False, PADDING)
        self.cloneSnapshotsHorBox.pack_end(self.cloneSnapshotsEntry, False, False, PADDING)
        self.linkedClonesHorBox.pack_end(self.linkedClonesEntry, False, False, PADDING)
        self.baseOutnameHorBox.pack_end(self.baseOutnameEntry, False, False, PADDING)
        self.vrdpBaseportHorBox.pack_end(self.vrdpBaseportEntry, False, False, PADDING)

# This class is the widget inside of vmWidget
class InternalnetBasenameWidget(Gtk.EventBox):

    def __init__(self):
        super(InternalnetBasenameWidget, self).__init__()

        self.outerHorBox = Gtk.Box(spacing=BOX_SPACING)

        self.label = Gtk.Label("Internalnet Basename:")
        self.entry = Gtk.Entry()

        self.initialize()

    def initialize(self):
        self.add(self.outerHorBox)

        self.outerHorBox.pack_start(self.label, False, False, PADDING)
        self.outerHorBox.pack_end(self.entry, False, False, PADDING)

# This class is a container that will hold the vm information
class VMWidget(Gtk.Box):

    def __init__(self):
        super(VMWidget, self).__init__()

        self.set_border_width(PADDING)

        # Declaration of boxes
        self.outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.nameHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.vrdpEnabledHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.iNetVerBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.inetBasenameWidgetList = []

        # Declaration of labels
        self.nameLabel = Gtk.Label("Name:")
        self.vrdpEnabledLabel = Gtk.Label("VRDP Enabled:")

        # Declaration of entrys
        self.nameEntry = Gtk.Entry()
        self.vrdpEnabledEntry = Gtk.Entry()

        self.initializeContainers()
        self.initializeLabels()
        self.initializeEntrys()

    def initializeContainers(self):
        self.add(self.outerVertBox)
        self.outerVertBox.add(self.nameHorBox)
        self.outerVertBox.add(self.vrdpEnabledHorBox)
        self.outerVertBox.add(self.iNetVerBox)

    def initializeLabels(self):
        self.nameHorBox.pack_start(self.nameLabel, False, False, PADDING)
        self.vrdpEnabledHorBox.pack_start(self.vrdpEnabledLabel, False, False, PADDING)

    def initializeEntrys(self):
        self.nameHorBox.pack_end(self.nameEntry, False, False, PADDING)
        self.vrdpEnabledHorBox.pack_end(self.vrdpEnabledEntry, False, False, PADDING)

    def loadInets(self, internalNetList):

        # Clear the box of widgets
        for widget in self.iNetVerBox.get_children():
            self.iNetVerBox.remove(widget)

        # Clear the list of widgets
        self.inetBasenameWidgetList = []

        for internalNet in internalNetList:
            inetWidget = InternalnetBasenameWidget()
            inetWidget.entry.set_text(internalNet)

            self.inetBasenameWidgetList.append(inetWidget)
            self.iNetVerBox.pack_start(inetWidget, False, False, 0)

    def initializeSignals(self, eventHandler):
        for widget in self.inetBasenameWidgetList:
            widget.connect("button-press-event", eventHandler)

    def addInet(self, eventHandler):
        inet = InternalnetBasenameWidget()
        inet.connect("button-press-event", eventHandler)
        self.inetBasenameWidgetList.append(inet)
        self.iNetVerBox.pack_start(inet, False, False, 0)

    def removeInet(self, inetWidget):

        if len(self.inetBasenameWidgetList) > 1:
            self.iNetVerBox.remove(inetWidget)
            self.inetBasenameWidgetList.remove(inetWidget)

# This class is a widget that is a grid, it holds the structure of the tree view
class WorkshopTreeWidget(Gtk.Grid):

    def __init__(self):
        super(WorkshopTreeWidget, self).__init__()

        self.set_border_width(PADDING)

        # Initialized fields
        self.treeStore = Gtk.TreeStore(str)
        self.treeView = Gtk.TreeView(self.treeStore)
        self.scrollableTreeList = Gtk.ScrolledWindow()
        self.initializeContainers()
        self.drawTreeView()
        self.setLayout()

    def initializeContainers(self):
        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)

    def populateTreeStore(self, workshopList):

        for workshop in workshopList:
            treeIter = self.treeStore.append(None, [workshop.filename])

            for vm in workshop.vmList:
                self.treeStore.append(treeIter, [vm.name])

    def clearTreeStore(self):
        self.treeStore.clear()

    def addNode(self, workshopName, vmName):
        treeIter = self.treeStore.append(None, [workshopName])
        self.treeStore.append(treeIter, [vmName])

    def addChildNode(self, workshopTreeIter, vmName):
        self.treeStore.append(self.treeStore.iter_parent(workshopTreeIter), [vmName])

    def drawTreeView(self):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Workshops", renderer, text=0)
        self.treeView.append_column(column)

    def setLayout(self):
        self.scrollableTreeList.set_min_content_width(200)
        self.scrollableTreeList.set_vexpand(True)
        self.attach(self.scrollableTreeList, 0, 0, 4, 10)
        self.scrollableTreeList.add(self.treeView)

# This class contains the main window, its main container is a notebook
class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super(AppWindow, self).__init__(*args, **kwargs)

        # Layout container initialization
        self.windowBox = Gtk.Box(spacing=BOX_SPACING)
        self.actionBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.actionEventBox = Gtk.EventBox()
        self.scrolledActionBox = Gtk.ScrolledWindow()
        self.scrolledInnerBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)

        # Widget creation
        self.workshopTree = WorkshopTreeWidget()
        self.baseWidget = BaseWidget()
        self.vmWidget = VMWidget()

        # Workshop config file list
        self.workshopList = []

        self.currentWorkshop = None
        self.currentVM = None
        self.isParent = None

        # Initialization
        self.initializeContainers()
        self.loadXMLFiles(WORKSHOP_CONFIG_DIRECTORY)
        self.workshopTree.populateTreeStore(self.workshopList)

        # Signal initialization
        # This will handle when the tree selection is changed
        select = self.workshopTree.treeView.get_selection()
        select.connect("changed", self.onItemSelected)

        # This is the signal for the file chooser under the vbox path
        self.baseWidget.chooseVBoxPathButton.connect("clicked", self.onVBoxPathClicked)

        # This will get called when the window terminates
        self.connect("delete-event", self.on_delete)

        # This is called when the action box is clicked
        #self.actionEventBox.connect("button-press-event", self.actionBoxEvent)
        # This will be the menu for adding and taking away iNetEntryList
        self.inetMenu = Gtk.Menu()
        addInet = Gtk.MenuItem("Add INet")
        addInet.connect("activate", self.addInetEventHandler)
        self.inetMenu.append(addInet)
        removeInet = Gtk.MenuItem("Remove INet")
        removeInet.connect("activate", self.removeInetEventHandler)
        self.inetMenu.append(removeInet)

        # Currentwidget in focus
        self.focusedInetWidget = None

        # Here we will initialize signals for the tree view right clicked
        self.workshopTree.treeView.connect("button-press-event", self.treeViewActionEvent)
        self.focusedTreeIter = None

        # Here we will have all the menu items
        self.addWorkshop = Gtk.MenuItem("Add Workshop")
        self.addWorkshop.connect("activate", self.addWorkshopActionEvent)
        self.removeWorkshop = Gtk.MenuItem("Remove Workshop")
        self.removeWorkshop.connect("activate", self.removeWorkshopActionEvent)
        self.exportWorkshop = Gtk.MenuItem("Export Workshop")
        self.exportWorkshop.connect("activate", self.exportWorkshopActionEvent)

        self.addVM = Gtk.MenuItem("Add VM")
        self.addVM.connect("activate", self.addVMActionEvent)
        self.removeVM = Gtk.MenuItem("Remove VM")
        self.removeVM.connect("activate", self.removeVMActionEvent)


        # Workshop context menu
        self.workshopMenu = Gtk.Menu()
        self.workshopMenu.append(self.addWorkshop)
        self.workshopMenu.append(self.removeWorkshop)
        self.workshopMenu.append(self.exportWorkshop)

        # VM context menu
        self.vmMenu = Gtk.Menu()
        self.vmMenu.append(self.addVM)
        self.vmMenu.append(self.removeVM)

    def initializeContainers(self):
        self.add(self.windowBox)

        self.windowBox.pack_start(self.workshopTree, False, False, PADDING)
        self.windowBox.pack_start(self.actionEventBox, False, False, PADDING)

        self.actionEventBox.add(self.actionBox)
        self.actionBox.pack_start(self.scrolledActionBox, False, False, PADDING)

        self.scrolledActionBox.add(self.scrolledInnerBox)
        self.scrolledActionBox.set_min_content_width(400)
        self.scrolledActionBox.set_min_content_height(600)

    # This will load xml files
    def loadXMLFiles(self, directory):

        # Here we will iterate through all the files that end with .xml
        #in the workshop_configs directory
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                workshop = Workshop()
                workshop.loadFileConfig(filename)
                self.workshopList.append(workshop)

    def onItemSelected(self, selection):
        model, treeiter = selection.get_selected()

        if treeiter == None:
            return

        self.softSave()

        if model.iter_has_child(treeiter):
            self.isParent = True
            filename = model[treeiter][0]
            self.currentWorkshop = None
            matchFound = False

            for workshop in self.workshopList:
                if filename == workshop.filename:
                    self.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return

            # The clicked row in the tree was valid so we will need to
            # clear all children in the main container and add the new one
            for widget in self.scrolledInnerBox.get_children():
                self.scrolledInnerBox.remove(widget)

            self.scrolledInnerBox.pack_start(self.baseWidget, False, False, PADDING)

            self.baseWidget.vBoxManageEntry.set_text(self.currentWorkshop.pathToVBoxManage)
            self.baseWidget.ipAddressEntry.set_text(self.currentWorkshop.ipAddress)
            self.baseWidget.baseGroupNameEntry.set_text(self.currentWorkshop.baseGroupName)
            self.baseWidget.numClonesEntry.set_text(self.currentWorkshop.numOfClones)
            self.baseWidget.cloneSnapshotsEntry.set_text(self.currentWorkshop.cloneSnapshots)
            self.baseWidget.linkedClonesEntry.set_text(self.currentWorkshop.linkedClones)
            self.baseWidget.baseOutnameEntry.set_text(self.currentWorkshop.baseOutName)
            self.baseWidget.vrdpBaseportEntry.set_text(self.currentWorkshop.vrdpBaseport)

            self.actionBox.show_all()

        elif not model.iter_has_child(treeiter):
            self.isParent = False
            vmName = model[treeiter][0]
            treeiter = model.iter_parent(treeiter)
            filename = model[treeiter][0]
            self.currentWorkshop = None
            matchFound = False

            for workshop in self.workshopList:
                if filename == workshop.filename:
                    self.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return

            self.currentVM = None
            matchFound = False
            for vmWidget in self.currentWorkshop.vmList:
                if vmName == vmWidget.name:
                    self.currentVM = vmWidget
                    matchFound = True
                    break

            if not matchFound:
                return

            for widget in self.scrolledInnerBox.get_children():
                self.scrolledInnerBox.remove(widget)

            self.scrolledInnerBox.pack_start(self.vmWidget, False, False, PADDING)

            self.vmWidget.nameEntry.set_text(self.currentVM.name)
            self.vmWidget.vrdpEnabledEntry.set_text(self.currentVM.vrdpEnabled)
            self.vmWidget.loadInets(self.currentVM.internalnetBasenameList)
            self.vmWidget.initializeSignals(self.inetActionEvent)

            self.actionBox.show_all()

    # This handles clicking the vboxpath
    def onVBoxPathClicked(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
        Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_filename(self.baseWidget.vBoxManageEntry.get_text())
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.baseWidget.vBoxManageEntry.set_text(dialog.get_filename())
            #self.actionBox.show_all()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel was selected")

        dialog.destroy()

    # Will save all changes to ram
    def softSave(self):

        if self.isParent == True:
            self.currentWorkshop.pathToVBoxManage = self.baseWidget.vBoxManageEntry.get_text()
            self.currentWorkshop.ipAddress = self.baseWidget.ipAddressEntry.get_text()
            self.currentWorkshop.baseGroupName = self.baseWidget.baseGroupNameEntry.get_text()
            self.currentWorkshop.numOfClones = self.baseWidget.numClonesEntry.get_text()
            self.currentWorkshop.cloneSnapshots = self.baseWidget.cloneSnapshotsEntry.get_text()
            self.currentWorkshop.linkedClones = self.baseWidget.linkedClonesEntry.get_text()
            self.currentWorkshop.baseOutName = self.baseWidget.baseOutnameEntry.get_text()
            self.currentWorkshop.vrdpBaseport = self.baseWidget.vrdpBaseportEntry.get_text()

        elif self.isParent == False:

            self.currentVM.name = self.vmWidget.nameEntry.get_text()
            self.currentVM.vrdpEnabled = self.vmWidget.vrdpEnabledEntry.get_text()

            self.currentVM.internalnetBasenameList = []
            for inetWidget in self.vmWidget.inetBasenameWidgetList:
                self.currentVM.internalnetBasenameList.append(inetWidget.entry.get_text())

    # Will save all changed to the disk
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

            # Create tree for writing to XML file
            tree = etree.ElementTree(root)

            # Write tree to XML config file
            tree.write(WORKSHOP_CONFIG_DIRECTORY+workshop.filename+".xml", pretty_print = True)

    # Performs a softsave then a hardsave
    def fullSave(self):
        self.softSave()
        self.hardSave()

    def inetActionEvent(self, widget, event):
        if event.button == 3:

            self.focusedInetWidget = widget

            self.inetMenu.show_all()
            self.inetMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def addInetEventHandler(self, menuItem):
        self.vmWidget.addInet(self.inetActionEvent)
        self.actionBox.show_all()

    def removeInetEventHandler(self, menuItem):
        self.vmWidget.removeInet(self.focusedInetWidget)
        self.actionBox.show_all()

    def treeViewActionEvent(self, treeView, event):
        # Get the current treeview model
        model = self.workshopTree.treeStore

        if event.button == 3:
            pathInfo= treeView.get_path_at_pos(event.x, event.y)

            if pathInfo is not None:
                path, column, xCoord, yCoord = pathInfo
                treeIter = model.get_iter(path)
                self.focusedTreeIter = treeIter
                #print(model[treeIter][0])
                if model.iter_has_child(treeIter):
                    self.workshopMenu.show_all()
                    self.workshopMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

                elif not model.iter_has_child(treeIter):
                    self.vmMenu.show_all()
                    self.vmMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def addNewWorkshop(self, workshopName, vmName):
        workshop = Workshop()
        workshop.filename = workshopName

        workshop.filename = workshopName
        workshop.pathToVBoxManage = "Path To VBoxManage"
        workshop.ipAddress = "IP Address"
        workshop.baseGroupName = "Base Group Name"
        workshop.numOfClones = "Number of Clones"
        workshop.cloneSnapshots = "Clone Snapshots"
        workshop.linkedClones = "Linked Clones"
        workshop.baseOutName = "Base Outname"
        workshop.vrdpBaseport = "VRDP Baseport"

        vm = VM()
        vm.name = vmName
        vm.vrdpEnabled = "VRDP Enabled"
        vm.internalnetBasenameList.append("intnet")
        workshop.vmList.append(vm)

        self.workshopList.append(workshop)
        self.workshopTree.addNode(workshop.filename, vm.name)

        self.softSave()
        self.hardSave()

    def addNewVM(self, vmName):
        vm = VM()
        vm.name = vmName
        vm.vrdpEnabled = "VRDP Enabled"
        vm.internalnetBasenameList.append("intnet")

        self.currentWorkshop.vmList.append(vm)
        self.workshopTree.addChildNode(self.focusedTreeIter, vm.name)

        self.softSave()
        self.hardSave()

    def addWorkshopActionEvent(self, menuItem):
        workshopDialog = EntryDialog(self, "Enter a workshop name.")
        workshopText = None

        while workshopDialog.status != True:
            response = workshopDialog.run()
            workshopText = workshopDialog.entryText
        workshopDialog.destroy()

        if workshopText != None:
            vmDialog = ListEntryDialog(self, "Enter a VM name.")
            vmText = None

            while not vmDialog.status == True:
                response = vmDialog.run()
                vmText = vmDialog.entryText
            vmDialog.destroy()

        if workshopText != None and vmText != None:
            self.addNewWorkshop(workshopText, vmText)

    def removeWorkshopActionEvent(self, menuItem):
        model = self.workshopTree.treeStore
        os.remove(WORKSHOP_CONFIG_DIRECTORY+"/"+self.currentWorkshop.filename+".xml")
        self.workshopList.remove(self.currentWorkshop)
        model.remove(self.focusedTreeIter)

    def addVMActionEvent(self, menuItem):
        vmDialog = ListEntryDialog(self, "Enter a VM name.")
        vmText = None

        while not vmDialog.status == True:
            response = vmDialog.run()
            vmText = vmDialog.entryText
        vmDialog.destroy()

        if vmText != None:
            self.addNewVM(vmText)

    def removeVMActionEvent(self, menuItem):
        if len(self.currentWorkshop.vmList) > 1:
            model = self.workshopTree.treeStore
            self.currentWorkshop.vmList.remove(self.currentVM)
            model.remove(self.focusedTreeIter)

    # Event, executes when export is called
    def exportWorkshopActionEvent(self, menuItem):

        vmList = subprocess.check_output([VBOXMANAGE_DIRECTORY, "list", "vms"])
        vmList = re.findall("\"(.*)\"", vmList)

        for vm in self.currentWorkshop.vmList:
            matchFound = False
            for registeredVM in vmList:
                if vm.name == registeredVM:
                    matchFound = True
                    break
                matchFound = False

        if not matchFound:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "Not all VM's for this workshop are registered.")
            dialog.run()
            dialog.destroy()
            return


        dialog = Gtk.FileChooserDialog("Please choose a folder.", self,
        Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        folderPath = None

        #total = len(self.currentWorkshop.vmList) * 11

        #currentTotal = []
        #currentTotal.append(0)

        if response == Gtk.ResponseType.OK:
            folderPath = dialog.get_filename()+"/"+self.currentWorkshop.filename
            dialog.destroy()

            if not os.path.exists(folderPath):
                os.makedirs(folderPath)

            for vm in self.currentWorkshop.vmList:
                #p = subprocess.Popen([VBOXMANAGE_DIRECTORY, "export", vm.name, "-o", folderPath+"/"+vm.name+".ova"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                #t = threading.Thread(target=self.exportWorker, args=[p, vm.name, currentTotal])
                #t.start()

                progress = LoggingDialog(self, "Export", [VBOXMANAGE_DIRECTORY, "export", vm.name, "-o", folderPath+"/"+vm.name+".ova"])
                progress.run()

            shutil.copy2("workshop_creator_gui_resources/workshop_configs/"+self.currentWorkshop.filename+".xml", folderPath)
            spinnerDialog = SpinnerDialog(self, "Zipping files, this may take a few minutes...")
            t = threading.Thread(target=self.zipWorker, args=[folderPath, spinnerDialog])
            t.start()
            spinnerDialog.run()
            shutil.rmtree(folderPath)
            gui_utilities.WarningDialog(self, "Export completed.")

        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    # Thread function, exports to file
    def exportWorker(self, process, workerID, currentTotal):

        character = None
        while process.poll() is None and character != "":
            character = process.stdout.read(1)
            if character == "%":
                currentTotal[0] = currentTotal[0] + 1

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

    # Event, executes when import is called
    def importActionEvent(self):
        dialog = Gtk.FileChooserDialog("Please choose the zip you wish to import.", self,
        Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        zipPath = None

        if response == Gtk.ResponseType.OK:
            zipPath = dialog.get_filename()
            tempPath = zipPath+"/../creatorImportTemp/"+os.path.splitext(os.path.basename(zipPath))[0]+"/"
            baseTempPath = zipPath+"/../creatorImportTemp/"
            dialog.destroy()

            # First we need to unzip the import file to a temp folder
            spinnerDialog = SpinnerDialog(self, "Unzipping files, this may take a few minutes...")
            t = threading.Thread(target=self.unzipWorker, args=[zipPath, spinnerDialog])
            t.start()
            spinnerDialog.run()

            ovaList = []
            xmlList = []
            # Get all files that end with .ova
            for filename in os.listdir(tempPath):
                if filename.endswith(".ova"):
                    ovaList.append(filename)
                elif filename.endswith(".xml"):
                    xmlList.append(filename)

            #total = len(ovaList) * 22

            #currentTotal = []
            #currentTotal.append(0)

            #threads = []
            for ova in ovaList:
                #p = subprocess.Popen([VBOXMANAGE_DIRECTORY, "import", tempPath+ova], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                #t = threading.Thread(target=self.importWorker, args=[p, currentTotal])
                #threads.append(t)
                #t.start()

                progress = LoggingDialog(self, "Import", [VBOXMANAGE_DIRECTORY, "import", tempPath+ova])
                progress.run()

            for xml in xmlList:
                shutil.copy2(tempPath+xml, WORKSHOP_CONFIG_DIRECTORY)
                shutil.rmtree(baseTempPath)



        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    # Thread function, imports files
    def importWorker(self, process, currentTotal):

        character = None
        while process.poll() is None and character != "":
            character = process.stdout.read(1)
            if character == "%":
                currentTotal[0] = currentTotal[0] + 1

    # Thread function, performs unzipping operation
    def unzipWorker(self, zipPath, spinnerDialog):
        unzip = zipfile.ZipFile(zipPath, 'r')
        unzip.extractall(zipPath+"/../creatorImportTemp")
        unzip.close()
        spinnerDialog.destroy()

    # Executes when the window is closed
    def on_delete(self, event, widget):
        self.fullSave()

# This class is the main application
class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, application_id="workshop.creator.gui",
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("new", None)
        action.connect("activate", self.onNew)
        self.add_action(action)

        action = Gio.SimpleAction.new("save", None)
        action.connect("activate", self.onSave)
        self.add_action(action)

        action = Gio.SimpleAction.new("run", None)
        action.connect("activate", self.onRun)
        self.add_action(action)

        action = Gio.SimpleAction.new("import", None)
        action.connect("activate", self.onImport)
        self.add_action(action)

        builder = Gtk.Builder.new_from_file(GUI_MENU_DESCRIPTION_DIRECTORY)
        self.set_menubar(builder.get_object("menubar"))

    def do_activate(self):
        Gtk.Application.do_activate(self)
        if not self.window:
            self.window = AppWindow(application=self, title="Workshop Creator GUI")
        self.window.present()
        self.window.show_all()

    def onNew(self, action, param):
        self.window.addWorkshopActionEvent(None)

    def onSave(self, action, param):
        self.window.fullSave()

    def onRun(self, action, param):
        if self.window.currentWorkshop is None:
            gui_utilities.WarningDialog(self.window, "You must select a workshop before you can run the creator.")
            return

        workshopName = self.window.currentWorkshop.filename
        command = ["python", WORKSHOP_CREATOR_DIRECTORY, WORKSHOP_CONFIG_DIRECTORY+workshopName+".xml"]
        loggingDialog = LoggingDialog(self.window, "Workshop Creator", command)
        loggingDialog.run()

    def onImport(self, action, param):
        self.window.importActionEvent()
        self.window.fullSave()
        self.window.destroy()
        self.window = AppWindow(application=self, title="Workshop Creator GUI")
        self.window.present()
        self.window.show_all()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
