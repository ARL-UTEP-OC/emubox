import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Constants
BOX_SPACING = 5
PADDING = 5

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

        # Declaration of buttons
        self.newButton = Gtk.Button(label="New")
        self.openButton = Gtk.Button(label="Open")
        self.saveButton = Gtk.Button(label="Save")

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

        self.initializeContainers()
        #self.initializeButtons()
        self.initializeLabels()
        self.initializeEntrys()

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


    def initializeButtons(self):
        self.newButton.connect("clicked", self.newButtonClicked)
        self.buttonsHorBox.pack_start(self.newButton, False, False, PADDING)

        self.openButton.connect("clicked", self.openButtonClicked)
        self.buttonsHorBox.pack_start(self.openButton, False, False, PADDING)

        self.saveButton.connect("clicked", self.saveButtonClicked)
        self.buttonsHorBox.pack_start(self.saveButton, False, False, PADDING)

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
        self.vBoxManageHorBox.pack_start(self.vBoxManageEntry, False, False, PADDING)
        self.ipAddressHorBox.pack_start(self.ipAddressEntry, False, False, PADDING)
        self.baseGroupNameHorBox.pack_start(self.baseGroupNameEntry, False, False, PADDING)
        self.numClonesHorBox.pack_start(self.numClonesEntry, False, False, PADDING)
        self.cloneSnapshotsHorBox.pack_start(self.cloneSnapshotsEntry, False, False, PADDING)
        self.linkedClonesHorBox.pack_start(self.linkedClonesEntry, False, False, PADDING)
        self.baseOutnameHorBox.pack_start(self.baseOutnameEntry, False, False, PADDING)
        self.vrdpBaseportHorBox.pack_start(self.vrdpBaseportEntry, False, False, PADDING)

    # Event handler functions
    def newButtonClicked(self, widget):
        print("New Button Clicked")

    def openButtonClicked(self, widget):
        print("Open Button Clicked")

    def saveButtonClicked(self, widget):
        print("Save Button Clicked")

# This class is a container that will hold the vm information
class VMWidget(Gtk.Box):

    def __init__(self):
        super(VMWidget, self).__init__()

        self.set_border_width(PADDING)

        # Declaration of boxes
        self.outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.nameHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.vrdpEnabledHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.internalnetBasenameHorBox = Gtk.Box(spacing=BOX_SPACING)

        # Declaration of labels
        self.nameLabel = Gtk.Label("Name:")
        self.vrdpEnabledLabel = Gtk.Label("VRDP Enabled:")
        self.internalnetBasenameLabel = Gtk.Label("Intrnalnet Basename:")

        # Declaration of entrys
        self.nameEntry = Gtk.Entry()
        self.vrdpEnabledEntry = Gtk.Entry()
        self.intenralnetBasenameEntry = Gtk.Entry()

        self.initializeContainers()
        self.initializeLabels()
        self.initializeEntrys()

    def initializeContainers(self):
        self.add(self.outerVertBox)
        self.outerVertBox.add(self.nameHorBox)
        self.outerVertBox.add(self.vrdpEnabledHorBox)
        self.outerVertBox.add(self.internalnetBasenameHorBox)

    def initializeLabels(self):
        self.nameHorBox.pack_start(self.nameLabel, False, False, PADDING)
        self.vrdpEnabledHorBox.pack_start(self.vrdpEnabledLabel, False, False, PADDING)
        self.internalnetBasenameHorBox.pack_start(self.internalnetBasenameLabel, False, False, PADDING)

    def initializeEntrys(self):
        self.nameHorBox.pack_start(self.nameEntry, False, False, PADDING)
        self.vrdpEnabledHorBox.pack_start(self.vrdpEnabledEntry, False, False, PADDING)
        self.internalnetBasenameHorBox.pack_start(self.intenralnetBasenameEntry, False, False, PADDING)

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
        self.populateTreeStore()
        self.drawTreeView()
        self.setLayout()

    def initializeContainers(self):
        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)

    def populateTreeStore(self):
        treeiter = self.treeStore.append(None, ["MainWorkshops"])
        self.treeStore.append(treeiter, ["SubWorkshop1"])
        self.treeStore.append(treeiter, ["SubWorkshop2"])
        treeiter = self.treeStore.append(None, ["MoreWorkshops"])
        self.treeStore.append(treeiter, ["SubWorkshop1"])
        self.treeStore.append(treeiter, ["SubWorkshop2"])

    def drawTreeView(self):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Workshops", renderer, text=0)
        self.treeView.append_column(column)

    def setLayout(self):
        self.scrollableTreeList.set_min_content_width(175)
        self.scrollableTreeList.set_vexpand(True)
        self.attach(self.scrollableTreeList, 0, 0, 4, 10)
        self.scrollableTreeList.add(self.treeView)

# This class contains the main window, its main container is a notebook
class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Workshop Creator GUI")

        self.windowBox = Gtk.Box(spacing=BOX_SPACING)

        self.workshopTree = WorkshopTreeWidget()
        self.baseWidget = BaseWidget()

        self.initializeContainers()

    def initializeContainers(self):
        self.add(self.windowBox)
        self.windowBox.pack_start(self.workshopTree, False, False, PADDING)
        self.windowBox.pack_start(self.baseWidget, False, False, PADDING)

def main():
    win = MainWindow()
    win.resize(500, 600)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__": main()
