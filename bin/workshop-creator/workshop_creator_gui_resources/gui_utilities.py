from __future__ import division
import os
import sys
import subprocess
import re
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk, GObject

import gui_constants as gui_constants

# Constants
BOX_SPACING = gui_constants.BOX_SPACING
PADDING = gui_constants.PADDING
WORKSHOP_CONFIG_DIRECTORY = gui_constants.WORKSHOP_CONFIG_DIRECTORY
GUI_MENU_DESCRIPTION_DIRECTORY = gui_constants.GUI_MENU_DESCRIPTION_DIRECTORY
VBOXMANAGE_DIRECTORY = gui_constants.VBOXMANAGE_DIRECTORY
WORKSHOP_CREATOR_DIRECTORY = gui_constants.WORKSHOP_CREATOR_DIRECTORY


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

class LoggingDialog(Gtk.Dialog):

    def __init__(self, parent, workshopName):
        Gtk.Dialog.__init__(self, "Workshop Wizard", parent, 0,
            (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(500, 500)
        self.set_deletable(False)

        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()

        self.scrollableWindow = Gtk.ScrolledWindow()
        self.scrollableWindow.set_min_content_width(400)
        self.scrollableWindow.set_min_content_height(450)

        self.dialogBox.add(self.scrollableWindow)

        self.textView = Gtk.TextView()
        self.textView.set_editable(False)
        self.textView.set_cursor_visible(False)
        self.textView.set_wrap_mode(True)
        self.scrollableWindow.add(self.textView)
        self.textBuffer = self.textView.get_buffer()

        self.set_response_sensitive(Gtk.ResponseType.OK, False)
        self.connect("response", self.dialogResponseActionEvent)
        self.show_all()

        self.process = subprocess.Popen(["python", WORKSHOP_CREATOR_DIRECTORY, WORKSHOP_CONFIG_DIRECTORY+workshopName+".xml"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.t = threading.Thread(target=self.runWorker, args=[self.process])
        self.t.start()

    def runWorker(self, process):
        end = self.textBuffer.get_end_iter()
        self.textBuffer.insert(end, "Starting Workshop Creator...\n")
        for line in iter(process.stdout.readline, b''):
            end = self.textBuffer.get_end_iter()
            line = line.strip()+"\n"
            # idle_add is needed for a thread-safe function, without it an assertion error will occur
            GObject.idle_add(self.addLine, line)
        end = self.textBuffer.get_end_iter()
        self.textBuffer.insert(end, "Workshop Creator Finished...\n")
        self.set_response_sensitive(Gtk.ResponseType.OK, True)

    def addLine(self, line):
        end = self.textBuffer.get_end_iter()
        self.textBuffer.insert(end, line)

    def dialogResponseActionEvent(self, dialog, responseID):
        # OK was clicked and there is text
        if responseID == Gtk.ResponseType.OK and self.process.poll() is not None:
            self.destroy()


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
