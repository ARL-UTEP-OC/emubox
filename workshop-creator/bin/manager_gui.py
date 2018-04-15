import gi; gi.require_version('Gtk', '3.0')
import workshop_creator_gui_resources.gui_constants as gui_constants
from gi.repository import Gtk
from workshop_creator_gui_resources.process_window import ProcessWindow


MANAGER_INSTANTIATOR_DIRECTORY = gui_constants.MANAGER_INSTANTIATOR_DIRECTORY


class ManagerWindow(Gtk.Window):

    def __init__(self, *args, **kwargs):
        super(ManagerWindow, self).__init__(*args, **kwargs)

        num_clients = 0
        workshops_running = []
        vms = []

        self.set_default_size(250, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        notebook = Gtk.Notebook()
        self.add(notebook)

        creator_page = Gtk.Box()
        creator_place_holder = Gtk.Label("CREATOR_HERE")
        creator_page.add(creator_place_holder)
        notebook.append_page(creator_page, Gtk.Label("Creator"))

        grid = Gtk.Grid()
        notebook.append_page(grid, Gtk.Label("Manager"))

        start_manager_button = Gtk.Button(label="Start Manager")
        start_manager_button.connect("clicked", self.startManagerActionEvent)
        grid.attach(start_manager_button, 0, 0, width=1, height=1)

        num_clients_label = Gtk.Label("Number of clients connected: " + str(num_clients))
        num_clients_label.set_xalign(0)
        grid.attach(num_clients_label, 0, 1, width=1, height=1)

        workshop_running_label = Gtk.Label("Workshops Running: " + str(workshops_running))
        workshop_running_label.set_xalign(0)
        grid.attach(workshop_running_label, 0, 2, width=1, height=1)

        vms_label = Gtk.Label("VMs: " + str(vms))
        vms_label.set_xalign(0)
        grid.attach(vms_label, 0, 3, width=1, height=1)


    def startManagerActionEvent(self, startButton):
        command = ["python", MANAGER_INSTANTIATOR_DIRECTORY]
        ProcessWindow(command)

if __name__ == "__main__":
    window = ManagerWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    Gtk.main()
