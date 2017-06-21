import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Constants
BOX_SPACING = 5
PADDING = 5

# This class is a window that contains boxes to layout the widgets
class MainWindow(Gtk.Window):

    # Declaration of boxes
    outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
    buttonsHorBox = Gtk.Box(spacing=BOX_SPACING)
    vBoxManageHorBox = Gtk.Box(spacing=BOX_SPACING)
    ipAddressHorBox = Gtk.Box(spacing=BOX_SPACING)
    baseGroupNameHorBox = Gtk.Box(spacing=BOX_SPACING)
    numClonesHorBox = Gtk.Box(spacing=BOX_SPACING)
    cloneSnapshotsHorBox = Gtk.Box(spacing=BOX_SPACING)
    linkedClonesHorBox = Gtk.Box(spacing=BOX_SPACING)
    baseOutnameHorBox = Gtk.Box(spacing=BOX_SPACING)
    vrdpBaseportHorBox = Gtk.Box(spacing=BOX_SPACING)

    # Declaration of buttons
    newButton = Gtk.Button(label="New")
    openButton = Gtk.Button(label="Open")
    saveButton = Gtk.Button(label="Save")

    # Declaration of labels
    vBoxManageLabel = Gtk.Label("Path To VBoxManager:")
    ipAddressLabel = Gtk.Label("IP Address:")
    baseGroupNameLabel = Gtk.Label("Base Group Name:")
    numClonesLabel = Gtk.Label("Number of Clones:")
    cloneSnapshotsLabel = Gtk.Label("Clone Snapshots:")
    linkedClonesLabel = Gtk.Label("Linked Clones:")
    baseOutnameLabel = Gtk.Label("Base Outname:")
    vrdpBaseportLabel = Gtk.Label("VRDP Baseport:")

    # Declaration of entrys
    vBoxManageEntry = Gtk.Entry()
    ipAddressEntry = Gtk.Entry()
    baseGroupNameEntry = Gtk.Entry()
    numClonesEntry = Gtk.Entry()
    cloneSnapshotsEntry = Gtk.Entry()
    linkedClonesEntry = Gtk.Entry()
    baseOutnameEntry = Gtk.Entry()
    vrdpBaseportEntry = Gtk.Entry()

    def __init__(self):

        Gtk.Window.__init__(self, title="Workshop Creator GUI")

        self.initializeContainers()
        self.initializeButtons()
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

def main():
    win = MainWindow()
    win.resize(500, 600)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__": main()
