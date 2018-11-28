import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui.widgets.CommandWidget import CommandWidget
from src.gui_constants import BOX_SPACING


class CommandsWindow(Gtk.Window):

    def __init__(self, parent):
        logging.debug("Creating InetsDialog")
        Gtk.Window.__init__(self)
        self.set_default_size(500, 300)

        commandsList = ['cd /tmp', 'command 2', 'command 3']

        #Declare Entries
        saveButton = Gtk.Button(label="Save Changes")

        # Declare Containers
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_max_content_height(250)
        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        inet_ver_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Organize Containers
        scrolled_window.add(inet_ver_box)
        outer_box.pack_start(scrolled_window, True, True, 0)
        outer_box.pack_end(saveButton, False, False, 0)
        self.add(outer_box)

        for inet in commandsList:
            w = CommandWidget()
            w.entry.set_text(inet)
            inet_ver_box.pack_start(w, False, False, 0)

        self.show_all()
