import logging
import xml.etree.ElementTree as ET
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui.widgets.DownloadTreeWidget import DownloadTreeWidget
from src.gui_constants import BOX_SPACING, PADDING


class DownloadDialog(Gtk.Dialog):

    def __init__(self, parent, message, xmlString):
        logging.debug("Creating DownloadDialog")
        Gtk.Dialog.__init__(self, "Download a Workshop", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(600, 300)
        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()
        self.outerVertBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.dialogBox.add(self.outerVertBox)

        self.label = Gtk.Label(message)
        self.xmlString = xmlString
        self.workshopList = []
        self.nameList = []

        # Here we will place the tree view
        self.treeWidget = DownloadTreeWidget()

        self.entry = Gtk.Entry()
        self.entryText = None

        self.outerVertBox.pack_start(self.label, False, False, PADDING)
        self.outerVertBox.pack_start(self.treeWidget, True, True, PADDING)
        self.outerVertBox.pack_start(self.entry, False, False, PADDING)

        self.connect("response", self.dialogResponseActionEvent)
        self.show_all()
        self.status = None

        self.treeWidget.populateTreeStore(self.parseXMLList())
        select = self.treeWidget.treeView.get_selection()
        select.connect("changed", self.onItemSelected)

    def parseXMLList(self):
        logging.debug("Running parseXMLList on downloaded file")
        root = ET.fromstring(self.xmlString.replace('&', '&amp;'))
        self.workshopList = []
        for workshop in root.findall('workshop'):
            self.workshopList.append(workshop.find('name').text.rstrip().lstrip()+"\n"+workshop.find('description').text.rstrip().lstrip())
            self.nameList.append(workshop.find('name').text.rstrip().lstrip())

        return self.workshopList

    def onItemSelected(self, selection):
        model, treeiter = selection.get_selected()

        if treeiter == None:
            return

        selectionName = model[treeiter][0]
        foundIndex = self.workshopList.index(selectionName)
        self.entry.set_text(self.nameList[foundIndex])

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
            self.status = False
