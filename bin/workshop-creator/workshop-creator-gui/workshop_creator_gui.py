import os
import sys

from lxml import etree

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from workshop_creator_gui_loader import Workshop
from workshop_creator_gui_loader import VM

# Constants
BOX_SPACING = 5
PADDING = 5
WORKSHOP_CONFIG_DIRECTORY = "workshop_configs"

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
        self.internalnetBasenameHorBoxList = []
        self.iNetEntryList = []

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

    def initializeInternalNetBasenames(self, internalNetList):

        for widget in self.iNetVerBox.get_children():
            self.iNetVerBox.remove(widget)

        self.internalnetBasenameHorBoxList = []
        self.iNetEntryList = []

        for internalNet in internalNetList:
            iNetHorBox = Gtk.Box(spacing=BOX_SPACING)

            internalnetBasenameLabel = Gtk.Label("Intrnalnet Basename:")
            iNetEntry = Gtk.Entry()
            self.iNetEntryList.append(iNetEntry)
            iNetEntry.set_text(internalNet)

            iNetHorBox.pack_start(internalnetBasenameLabel, False, False, PADDING)
            iNetHorBox.pack_end(iNetEntry, False, False, PADDING)

            self.internalnetBasenameHorBoxList.append(iNetHorBox)

        for iNetBox in self.internalnetBasenameHorBoxList:
            self.iNetVerBox.pack_start(iNetBox, False, False, 0)


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
        select = self.workshopTree.treeView.get_selection()
        select.connect("changed", self.onItemSelected)

        self.baseWidget.chooseVBoxPathButton.connect("clicked", self.onVBoxPathClicked)

        # Called when this window terminates
        self.connect("delete-event", self.on_delete)

    def initializeContainers(self):
        self.add(self.windowBox)

        self.windowBox.pack_start(self.workshopTree, False, False, PADDING)
        self.windowBox.pack_start(self.actionBox, False, False, PADDING)

        self.actionBox.pack_start(self.scrolledActionBox, False, False, PADDING)

        self.scrolledActionBox.add(self.scrolledInnerBox)
        self.scrolledActionBox.set_min_content_width(400)
        self.scrolledActionBox.set_min_content_height(600)

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
            self.vmWidget.initializeInternalNetBasenames(self.currentVM.internalnetBasenameList)

            self.actionBox.show_all()

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
            for inet in self.vmWidget.iNetEntryList:
                self.currentVM.internalnetBasenameList.append(inet.get_text())

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
            tree.write("workshop_configs/"+workshop.filename+".xml", pretty_print = True)

    def fullSave(self):
        self.softSave()
        self.hardSave()

    def on_delete(self, event, widget):
        self.fullSave()


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

        builder = Gtk.Builder.new_from_file("menuDescription.xml")
        self.set_menubar(builder.get_object("menubar"))

    def do_activate(self):
        Gtk.Application.do_activate(self)
        if not self.window:
            self.window = AppWindow(application=self, title="Workshop Creator GUI")
        self.window.present()
        self.window.show_all()

    def onNew(self, action, param):
        print("New Menu Option Pressed")

    def onSave(self, action, param):
        self.window.fullSave()


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
