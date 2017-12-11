from __future__ import division
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
from gi.repository import GLib, Gio, Gtk, GObject, Gdk

from workshop_creator_gui_resources.model import Workshop
from workshop_creator_gui_resources.model import VM
from workshop_creator_gui_resources.model import Material
from workshop_creator_gui_resources.model import Session

import workshop_creator_gui_resources.gui_constants as gui_constants

# Constants
BOX_SPACING = gui_constants.BOX_SPACING
PADDING = gui_constants.PADDING
WORKSHOP_CONFIG_DIRECTORY = gui_constants.WORKSHOP_CONFIG_DIRECTORY
GUI_MENU_DESCRIPTION_DIRECTORY = gui_constants.GUI_MENU_DESCRIPTION_DIRECTORY
VBOXMANAGE_DIRECTORY = gui_constants.VBOXMANAGE_DIRECTORY
WORKSHOP_CREATOR_DIRECTORY = gui_constants.WORKSHOP_CREATOR_DIRECTORY
WORKSHOP_MATERIAL_DIRECTORY = gui_constants.WORKSHOP_MATERIAL_DIRECTORY
VM_TREE_LABEL = "V: "
MATERIAL_TREE_LABEL = "M: "


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
        self.numClonesEntry = Gtk.SpinButton()
        self.numClonesEntry.set_range(1, 50)
        self.numClonesEntry.set_increments(1, 5)
        self.cloneSnapshotsEntry = Gtk.ComboBoxText()
        self.cloneSnapshotsEntry.insert_text(0, "true")
        self.cloneSnapshotsEntry.insert_text(1, "false")
        self.linkedClonesEntry = Gtk.ComboBoxText()
        self.linkedClonesEntry.insert_text(0, "true")
        self.linkedClonesEntry.insert_text(1, "false")
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
        self.removeInetButton = Gtk.Button.new_with_label("-")

        self.initialize()

    def initialize(self):
        self.add(self.outerHorBox)

        self.outerHorBox.pack_start(self.label, False, False, PADDING)
        self.outerHorBox.pack_end(self.removeInetButton, False, False, PADDING)
        self.outerHorBox.pack_end(self.entry, False, False, PADDING)

# This class is a container that will hold the material information
class MaterialWidget(Gtk.Box):

    def __init__(self):
        super(MaterialWidget, self).__init__()

        self.set_border_width(PADDING)

        # Declaration of boxes
        self.outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.addressHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.nameHorBox = Gtk.Box(spacing=BOX_SPACING)

        # Declaration of labels
        self.nameLabel = Gtk.Label("Name:")

        # Declaration of entrys
        self.nameEntry = Gtk.Entry()

        #initialize containers
        self.add(self.outerVertBox)
        self.outerVertBox.add(self.addressHorBox)
        self.outerVertBox.add(self.nameHorBox)

        #initialize labels
        self.nameHorBox.pack_start(self.nameLabel, False, False, PADDING)

        #initialize entries
        self.nameHorBox.pack_end(self.nameEntry, False, False, PADDING)


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
        self.vrdpEnabledEntry = Gtk.ComboBoxText()
        self.vrdpEnabledEntry.insert_text(0, "true")
        self.vrdpEnabledEntry.insert_text(1, "false")
        self.addInetButton = Gtk.Button.new_with_label("Add Internalnet Basename")

        self.initializeContainers()
        self.initializeLabels()
        self.initializeEntrys()

    def initializeContainers(self):
        self.add(self.outerVertBox)
        self.outerVertBox.add(self.nameHorBox)
        self.outerVertBox.add(self.vrdpEnabledHorBox)
        self.outerVertBox.add(self.iNetVerBox)
        self.outerVertBox.add(self.addInetButton)

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

        self.sizeOfList=len(internalNetList)
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
        inet.entry.set_text("default_inet")
        inet.connect("button-press-event", eventHandler)
        self.inetBasenameWidgetList.append(inet)
        self.iNetVerBox.pack_start(inet, False, False, 0)

    def removeInet(self, inetNumber):

        if len(self.inetBasenameWidgetList) > 1:
            self.iNetVerBox.remove(self.inetBasenameWidgetList[inetNumber])
            self.inetBasenameWidgetList.remove(self.inetBasenameWidgetList[inetNumber])

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
                self.treeStore.append(treeIter, [VM_TREE_LABEL+vm.name])
            for material in workshop.materialList:
                self.treeStore.append(treeIter, [MATERIAL_TREE_LABEL+material.name])

    def clearTreeStore(self):
        self.treeStore.clear()

    def addNode(self, workshopName, vmName):
        treeIter = self.treeStore.append(None, [workshopName])
        self.treeStore.append(treeIter, [VM_TREE_LABEL+vmName])

    def addChildNode(self, workshopTreeIter, vmName):
        self.treeStore.append(workshopTreeIter, [vmName])

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

        #self.ld = LoggingDialog()
        #fix error when soft saving
        self.isRemoveVM = False

        # Layout container initialization
        self.windowBox = Gtk.Box(spacing=BOX_SPACING)
        self.actionBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.actionEventBox = Gtk.EventBox()
        self.scrolledActionBox = Gtk.ScrolledWindow()
        self.scrolledInnerBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)

        # Widget creation
        self.workshopTree = WorkshopTreeWidget()
        self.currentModel = None
        self.currentIter = None
        self.baseWidget = BaseWidget()
        self.vmWidget = VMWidget()
        self.materialWidget = MaterialWidget()

        # if the currently highlighted tree element is a parent, its a workshop
        self.isParent = None

        # Initialization
        self.initializeContainers()
        self.session=Session()
        self.workshopTree.populateTreeStore(self.session.workshopList)

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
        #removeInet = Gtk.MenuItem("Remove INet")
        #removeInet.connect("activate", self.removeInetEventHandler)
        #self.inetMenu.append(removeInet)

        self.vmWidget.addInetButton.connect("clicked", self.addInetEventHandler)



        # Currentwidget in focus
        self.focusedInetWidget = None

        # Here we will initialize signals for the tree view right clicked
        self.workshopTree.treeView.connect("button-press-event", self.treeViewActionEvent)
        self.focusedTreeIter = None

        # Here we will have all the menu items
        self.addWorkshop = Gtk.MenuItem("Add Workshop")
        self.addWorkshop.connect("activate", self.addWorkshopActionEvent)
        self.createWorkshop = Gtk.MenuItem("Create Clones")
        self.createWorkshop.connect("activate", self.runWorkshopActionEvent)
        self.removeWorkshop = Gtk.MenuItem("Remove Workshop")
        self.removeWorkshop.connect("activate", self.removeWorkshopActionEvent)
        self.exportWorkshop = Gtk.MenuItem("Export Workshop")
        self.exportWorkshop.connect("activate", self.exportWorkshopActionEvent)
        self.addVM = Gtk.MenuItem("Add VM")
        self.addVM.connect("activate", self.addVMActionEvent)
        self.addMaterial = Gtk.MenuItem("Add Material File")
        self.addMaterial.connect("activate", self.addMaterialActionEvent)
        self.createRDP = Gtk.MenuItem("Create RDP Files")
        self.createRDP.connect("activate", self.createRDPActionEvent)
        self.restoreSnapshots = Gtk.MenuItem("Restore Snapshots")
        self.restoreSnapshots.connect("activate", self.restoreSnapshotsActionEvent)

        self.removeItem = Gtk.MenuItem("Remove Workshop Item")
        self.removeItem.connect("activate", self.removeVMActionEvent)


        # Workshop context menu
        self.workshopMenu = Gtk.Menu()
        self.workshopMenu.append(self.addVM)
        self.workshopMenu.append(self.addMaterial)
        self.workshopMenu.append(Gtk.SeparatorMenuItem())
        self.workshopMenu.append(self.createWorkshop)
        self.workshopMenu.append(self.removeWorkshop)
        self.workshopMenu.append(self.exportWorkshop)
        self.workshopMenu.append(Gtk.SeparatorMenuItem())
        self.workshopMenu.append(self.createRDP)
        self.workshopMenu.append(self.restoreSnapshots)


        #context menu for blank space
        self.blankMenu = Gtk.Menu()
        self.blankMenu.append(self.addWorkshop)

        # VM context menu
        self.itemMenu = Gtk.Menu()
        self.itemMenu.append(self.removeItem)


    def initializeContainers(self):
        self.add(self.windowBox)

        self.windowBox.pack_start(self.workshopTree, False, False, PADDING)
        self.windowBox.pack_start(self.actionEventBox, False, False, PADDING)

        self.actionEventBox.add(self.actionBox)
        self.actionBox.pack_start(self.scrolledActionBox, False, False, PADDING)

        self.scrolledActionBox.add(self.scrolledInnerBox)
        self.scrolledActionBox.set_min_content_width(400)
        self.scrolledActionBox.set_min_content_height(600)

    def onItemSelected(self, selection):
        self.softSave()
        model, treeiter = selection.get_selected()
        self.currentModel = model
        self.currentIter = treeiter

        if treeiter == None:
            return


        if model.iter_has_child(treeiter):
            self.isParent = True
            filename = model[treeiter][0]
            self.session.currentWorkshop = None
            matchFound = False

            for workshop in self.session.workshopList:
                if filename == workshop.filename:
                    self.session.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return

            # The clicked row in the tree was valid so we will need to
            # clear all children in the main container and add the new one
            for widget in self.scrolledInnerBox.get_children():
                self.scrolledInnerBox.remove(widget)

            self.scrolledInnerBox.pack_start(self.baseWidget, False, False, PADDING)

            self.baseWidget.vBoxManageEntry.set_text(self.session.currentWorkshop.pathToVBoxManage)
            self.baseWidget.ipAddressEntry.set_text(self.session.currentWorkshop.ipAddress)
            self.baseWidget.baseGroupNameEntry.set_text(self.session.currentWorkshop.baseGroupName)
            self.baseWidget.numClonesEntry.set_value(int(float(self.session.currentWorkshop.numOfClones)))
            #self.baseWidget.cloneSnapshotsEntry.set_text(self.session.currentWorkshop.cloneSnapshots)
            self.holdClone=0
            if self.session.currentWorkshop.cloneSnapshots == "false":
                self.holdClone=1
            self.baseWidget.cloneSnapshotsEntry.set_active(self.holdClone)
            #self.baseWidget.linkedClonesEntry.set_text(self.session.currentWorkshop.linkedClones)
            self.holdClone=0
            if self.session.currentWorkshop.linkedClones == "false":
                self.holdClone=1
            self.baseWidget.linkedClonesEntry.set_active(self.holdClone)
            self.baseWidget.baseOutnameEntry.set_text(self.session.currentWorkshop.baseOutName)
            self.baseWidget.vrdpBaseportEntry.set_text(self.session.currentWorkshop.vrdpBaseport)

            self.actionBox.show_all()

        elif not model.iter_has_child(treeiter):
            self.isParent = False
            vmName = model[treeiter][0]
            treeiter = model.iter_parent(treeiter)
            filename = model[treeiter][0]
            self.session.currentWorkshop = None
            matchFound = False

            for workshop in self.session.workshopList:
                if filename == workshop.filename:
                    self.session.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return

            self.currentVM = None
            self.currentMaterial = None
            self.session.currentVM = None
            self.session.currentMaterial = None
            matchFound = False
            for vmWidget in self.session.currentWorkshop.vmList:
                if vmName == VM_TREE_LABEL+vmWidget.name:
                    self.session.currentVM = vmWidget
                    matchFound = True
                    break

            if not matchFound:
                for materialWidget in self.session.currentWorkshop.materialList:
                    if vmName == MATERIAL_TREE_LABEL+materialWidget.name:
                        self.session.currentMaterial = materialWidget
                        matchFound = True
                        break

            if not matchFound:
                return

            for widget in self.scrolledInnerBox.get_children():
                self.scrolledInnerBox.remove(widget)

            if self.session.currentVM != None:
                self.scrolledInnerBox.pack_start(self.vmWidget, False, False, PADDING)

                self.vmWidget.nameEntry.set_text(self.session.currentVM.name)
                self.holdVRDP=0
                if self.session.currentVM.vrdpEnabled == "false":
                    self.holdVRDP=1
                self.vmWidget.vrdpEnabledEntry.set_active(self.holdVRDP)
                self.vmWidget.loadInets(self.session.currentVM.internalnetBasenameList)
                self.vmWidget.initializeSignals(self.inetActionEvent)

                if len(self.vmWidget.inetBasenameWidgetList) > 1:
                    for k,rientry in enumerate(self.vmWidget.inetBasenameWidgetList):
                        rientry.removeInetButton.connect("clicked", self.removeInetEventHandler, k)

            elif self.session.currentMaterial != None:
                self.scrolledInnerBox.pack_start(self.materialWidget, False, False, PADDING)

                self.materialWidget.nameEntry.set_text(self.session.currentMaterial.name)

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
            self.holdSnaps="true"
            if self.baseWidget.cloneSnapshotsEntry.get_active_text() == "false":
                self.holdSnaps="false"
            self.holdLinked="true"
            if self.baseWidget.linkedClonesEntry.get_active_text() == "false":
                self.holdLinked="false"
            self.session.softSaveWorkshop(self.baseWidget.vBoxManageEntry.get_text(), self.baseWidget.ipAddressEntry.get_text(), self.baseWidget.baseGroupNameEntry.get_text(), str(self.baseWidget.numClonesEntry.get_value_as_int()), self.holdSnaps, self.holdLinked, self.baseWidget.baseOutnameEntry.get_text(), self.baseWidget.vrdpBaseportEntry.get_text())

        elif self.isParent == False:

            if self.session.currentVM != None:
                if not self.isRemoveVM:
                    self.currentModel.set(self.currentIter, 0, VM_TREE_LABEL+self.vmWidget.nameEntry.get_text())
                self.holdInternalnetBasenameList = []
                for inetWidget in self.vmWidget.inetBasenameWidgetList:
                    self.holdInternalnetBasenameList.append(inetWidget.entry.get_text())

                self.holdVRDP="true"
                if self.vmWidget.vrdpEnabledEntry.get_active_text() == "false":
                    self.holdVRDP="false"
                self.session.softSaveVM(self.vmWidget.nameEntry.get_text(), self.holdVRDP, self.holdInternalnetBasenameList)
            elif self.session.currentMaterial != None:
                if not self.isRemoveVM:
                    self.currentModel.set(self.currentIter, 0, MATERIAL_TREE_LABEL+self.materialWidget.nameEntry.get_text())
                self.session.softSaveMaterial(self.materialWidget.nameEntry.get_text())
            self.isRemoveVM = False


    # Will save all changed to the disk
    def hardSave(self):

        self.session.hardSave()

    # Performs a softsave then a hardsave
    def fullSave(self):
        self.softSave()
        self.hardSave()

    def createRDPActionEvent(self, menuItem):
        self.session.runScript("workshop-rdp.py")

    def restoreSnapshotsActionEvent(self, menuItem):
        self.session.runScript("workshop-restore.py")

    def inetActionEvent(self, widget, event):
        if event.button == 3:

            self.focusedInetWidget = widget

            self.inetMenu.show_all()
            self.inetMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def addInetEventHandler(self, menuItem):
        self.vmWidget.addInet(self.inetActionEvent)
        self.actionBox.show_all()

    def removeInetEventHandler(self, menuItem, *data):
        self.vmWidget.removeInet(data[0])
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
                    self.itemMenu.show_all()
                    self.itemMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

            else:
                self.blankMenu.show_all()
                self.blankMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def addNewWorkshop(self, workshopName, vmName):
        self.session.addWorkshop(workshopName, vmName)
        self.workshopTree.addNode(workshopName, vmName)

        self.softSave()
        self.hardSave()

    def addNewVM(self, vmName):
        self.session.addVM(vmName)
        self.workshopTree.addChildNode(self.focusedTreeIter, VM_TREE_LABEL+vmName)

        self.softSave()
        self.hardSave()

    def addNewMaterial(self, materialAddress):
        holdName = os.path.basename(materialAddress)
        self.session.addMaterial(materialAddress)
        self.workshopTree.addChildNode(self.focusedTreeIter, MATERIAL_TREE_LABEL+holdName)

    def runWorkshopActionEvent(self, menuItem):
        if self.session.currentWorkshop is None:
            WarningDialog(self.window, "You must select a workshop before you can run the workshop.")
            return

        workshopName = self.session.currentWorkshop.filename
        command = ["python", WORKSHOP_CREATOR_DIRECTORY, WORKSHOP_CONFIG_DIRECTORY+workshopName+".xml"]
        t = threading.Thread(target=os.system, args=['python "'+WORKSHOP_CREATOR_DIRECTORY+'" "'+WORKSHOP_CONFIG_DIRECTORY+workshopName+'.xml"'])
        t.start()

        self.session.runWorkshop()
        #        self.runLogging("Workshop Creator", command)
        #        t = threading.Thread(target=self.runLogging, args=["Workshop Creator", command])
        #            t.start()
        #        loggingDialog = LoggingDialog(self.window, "Workshop Creator", command)
        #        loggingDialog.run()

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
        d = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, "Are you sure you want to permanently delete this workshop?")
        response = d.run()
        d.destroy()

        if response == Gtk.ResponseType.OK:
            model = self.workshopTree.treeStore
            self.session.removeWorkshop()
            model.remove(self.focusedTreeIter)

    def addMaterialActionEvent(self, menuItem):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
        Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.addNewMaterial(dialog.get_filename())
            #self.actionBox.show_all()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel was selected")

        dialog.destroy()

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
        model = self.workshopTree.treeStore
        if self.session.currentVM != None:
            if len(self.session.currentWorkshop.vmList) > 1:
                self.session.removeVM()
                self.isRemoveVM=True
                model.remove(self.focusedTreeIter)
            else:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "Cannot delete the last VM in a Workshop.")
                dialog.run()
                dialog.destroy()

        elif self.session.currentMaterial != None:
            self.session.removeMaterial()
            self.isRemoveVM=True
            model.remove(self.focusedTreeIter)


    # Event, executes when export is called
    def exportWorkshopActionEvent(self, menuItem):

        matchFound = self.session.getAvailableVMs()

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
            folderPath = dialog.get_filename()+"/"+self.session.currentWorkshop.filename
            dialog.destroy()

            #holdLogging=[]
            spinnerDialog=SpinnerDialog(self, "Exporting VMs, this may take a few minutes...")
            #holdVMs=self.session.getCurrentVMList()
            t = threading.Thread(target=self.session.exportWorkshop, args=[folderPath, spinnerDialog])
            t.start()
            #for vm in holdVMs:
                #holdLogging.append(LoggingDialog(self, "Export", [VBOXMANAGE_DIRECTORY, "export", vm.name, "-o", folderPath+"/"+vm.name+".ova"]))
                #self.session.exportWorkshop(folderPath, spinnerDialog, spinnerDialog2)

        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

            #    def exportOVAs(self, holdVMs)
            #        for vm in holdVMs:
            #            os.system('"'+VBOXMANAGE_DIRECTORY+'" export "'+vm.name+'" -o "'+folderPath+'/'+vmname+'.ova"')
            #        self.session.exportWorkshop(folderPath

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
            self.session.importUnzip(zipPath, spinnerDialog)
            spinnerDialog.run()

            ovaList = []
            xmlList = []
            materialList = []
            rdpList = []
            # Get all files that end with .ova
            for filename in os.listdir(tempPath):
                if filename.endswith(".ova"):
                    ovaList.append(filename)
                elif filename.endswith(".xml"):
                    xmlList.append(filename)

            for filename in os.listdir(tempPath+"/Materials/"):
                materialList.append(filename)

            for filename in os.listdir(tempPath+"/RDP/"):
                rdpList.append(filename)


            for ova in ovaList:
                spinnerDialog = SpinnerDialog(self, "Importing to VBox...")
                self.session.importToVBox(tempPath+ova, spinnerDialog)

            for xml in xmlList:
                shutil.copy2(tempPath+xml, WORKSHOP_CONFIG_DIRECTORY)

            holdMatPath = WORKSHOP_MATERIAL_DIRECTORY+(os.path.splitext(xmlList[0])[0])+"/"
            if not os.path.exists(holdMatPath):
                os.makedirs(holdMatPath)
            for material in materialList:
                if not os.path.exists(holdMatPath+material):
                    shutil.copy2(tempPath+"/Materials/"+material, holdMatPath)

            holdRDPPath = WORKSHOP_RDP_DIRECTORY+(os.path.splitext(xmlList[0])[0])+"/"
            if not os.path.exists(holdRDPPath):
                os.makedirs(holdRDPPath)
            for rdp in rdpList:
                if not os.path.exists(holdRDPPath+rdp):
                    shutil.copy2(tempPath+"/RDP/"+rdp, holdRDPPath)


            self.session.loadXMLFiles(tempPath)
            self.workshopTree.clearTreeStore()
            self.workshopTree.populateTreeStore(self.session.workshopList)


            shutil.rmtree(baseTempPath)

        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    # Executes when the window is closed
    def on_delete(self, event, widget):
        self.fullSave()


        #    def runLogging(self, inName, command):
        #        loggingDialog = LoggingDialog(self, inName, command)
        #        loggingDialog.run()

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
        self.window.runWorkshopActionEvent(None)

    def onImport(self, action, param):
        self.window.importActionEvent()
        self.window.fullSave()
        self.window.destroy()
        self.window = AppWindow(application=self, title="Workshop Creator GUI")
        self.window.present()
        self.window.show_all()




# This class is a general message dialog with entry
class EntryDialog(Gtk.Dialog):

    def __init__(self, parent, message):
        Gtk.Dialog.__init__(self, "Workshop Wizard", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()
        self.outerVertBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)

        self.dialogBox.add(self.outerVertBox)

        self.label = Gtk.Label(message)
        self.entry = Gtk.Entry()
        self.entryText = None

        self.outerVertBox.pack_start(self.label, False, False, PADDING)
        self.outerVertBox.pack_start(self.entry, False, False, PADDING)
        self.set_modal(True)

        self.connect("response", self.dialogResponseActionEvent)

        self.show_all()

        self.status = None

    def dialogResponseActionEvent(self, dialog, responseID):
        # OK was clicked and there is text
        if responseID == Gtk.ResponseType.OK and not self.entry.get_text_length() < 1:
            self.entryText = self.entry.get_text()
            self.status = True

        # Ok was clicked and there is no text
        elif responseID == Gtk.ResponseType.OK and self.entry.get_text_length() < 1:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "The entry must not be empty.")
            dialog.run()
            dialog.destroy()

        # The operation was canceled
        elif responseID == Gtk.ResponseType.CANCEL or responseID == Gtk.ResponseType.DELETE_EVENT:
            self.entryText = None
            self.status = True

class VMTreeWidget(Gtk.Grid):

    def __init__(self):
        super(VMTreeWidget, self).__init__()

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

    def populateTreeStore(self, registeredVMList):
        for vm in registeredVMList:
            treeIter = self.treeStore.append(None, [vm])

    def drawTreeView(self):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Registered VM's", renderer, text=0)
        self.treeView.append_column(column)

    def setLayout(self):
        self.scrollableTreeList.set_min_content_width(100)
        self.scrollableTreeList.set_min_content_height(100)
        self.scrollableTreeList.set_vexpand(True)
        self.attach(self.scrollableTreeList, 0, 0, 4, 10)
        self.scrollableTreeList.add(self.treeView)

class ListEntryDialog(Gtk.Dialog):

    def __init__(self, parent, message):
        Gtk.Dialog.__init__(self, "Workshop Wizard", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(300, 300)
        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()
        self.outerVertBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.dialogBox.add(self.outerVertBox)

        self.label = Gtk.Label(message)

        # Here we will place the tree view
        self.treeWidget = VMTreeWidget()

        self.entry = Gtk.Entry()
        self.entryText = None

        self.outerVertBox.pack_start(self.label, False, False, PADDING)
        self.outerVertBox.pack_start(self.treeWidget, True, True, PADDING)
        self.outerVertBox.pack_start(self.entry, False, False, PADDING)

        self.connect("response", self.dialogResponseActionEvent)
        self.show_all()
        self.status = None

        self.treeWidget.populateTreeStore(self.retrieveVMList())
        select = self.treeWidget.treeView.get_selection()
        select.connect("changed", self.onItemSelected)

    def retrieveVMList(self):
        # If there are no VM's the list will be empty
        vmList = subprocess.check_output([VBOXMANAGE_DIRECTORY, "list", "vms"])
        vmList = re.findall("\"(.*)\"", vmList)
        return vmList

    def onItemSelected(self, selection):
        model, treeiter = selection.get_selected()

        if treeiter == None:
            return

        vmName = model[treeiter][0]
        self.entry.set_text(vmName)

    def dialogResponseActionEvent(self, dialog, responseID):
        # OK was clicked and there is text
        if responseID == Gtk.ResponseType.OK and not self.entry.get_text_length() < 1:
            self.entryText = self.entry.get_text()
            self.status = True

        # Ok was clicked and there is no text
        elif responseID == Gtk.ResponseType.OK and self.entry.get_text_length() < 1:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "The entry must not be empty.")
            dialog.run()
            dialog.destroy()

        # The operation was canceled
        elif responseID == Gtk.ResponseType.CANCEL or responseID == Gtk.ResponseType.DELETE_EVENT:
            self.entryText = None
            self.status = True

class ExportImportProgressDialog(Gtk.Dialog):
    def __init__(self, parent, message, currentTotal, total):
        Gtk.Dialog.__init__(self, "Workshop Wizard", parent, 0)

        self.set_default_size(50, 75)
        self.set_deletable(False)

        self.currentTotal = currentTotal
        self.total = total

        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()
        self.outerVerBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.dialogBox.add(self.outerVerBox)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        self.outerVerBox.pack_start(self.progressbar, False, False, PADDING)

        self.progressbar.set_text(message)

        self.timeout_id = GObject.timeout_add(1000, self.on_timeout, None)

        self.show_all()

    def on_timeout(self, user_data):

        new_value = self.currentTotal[0] / self.total

        if new_value >= 1:
            self.destroy()
            return False

        self.progressbar.set_fraction(new_value)

        # As this is a timeout function, return True so that it
        # continues to get called
        return True

class SpinnerDialog(Gtk.Dialog):

    def __init__(self, parent, message):
        Gtk.Dialog.__init__(self, "Workshop Wizard", parent, 0)

        self.set_deletable(False)

        self.dialogBox = self.get_content_area()
        self.outerVerBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.label = Gtk.Label(message)
        self.spinner = Gtk.Spinner()
        self.dialogBox.add(self.outerVerBox)
        self.outerVerBox.pack_start(self.label, False, False, PADDING)
        self.outerVerBox.pack_start(self.spinner, False, False, PADDING)

        self.show_all()
        self.spinner.start()

def WarningDialog(self, message):
    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, message)
    dialog.run()
    dialog.destroy()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
