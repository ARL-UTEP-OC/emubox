import threading
import ast
import gi; gi.require_version('Gtk', '3.0')
import workshop_creator_gui_resources.gui_constants as gui_constants
from subprocess import Popen, PIPE
from gi.repository import Gtk


MANAGER_BIN_DIRECTORY = gui_constants.MANAGER_BIN_DIRECTORY
PADDING = gui_constants.PADDING


class WorkshopListBoxRow(Gtk.ListBoxRow):
    def __init__(self, workshop):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = workshop
        self.add(Gtk.Label(str(workshop[0]) + "\t\t\t\t\t\t\t\tUnits Available: " + str(workshop[1])))


class ManagerBox(Gtk.Box):

    def __init__(self):
        super(ManagerBox, self).__init__()
        self.num_clients = 0
        self.workshops_running = []
        self.p = None

        self.set_border_width(PADDING)
        self.outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.outer_box.add(self.top_box)
        self.outer_box.add(self.bottom_box)

        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.top_box.pack_start(list_box, False, False, 0)

        manager_row = Gtk.ListBoxRow()
        manager_selection = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=475)
        manager_label = Gtk.Label("Manager", xalign=0)
        manager_selection.pack_start(manager_label, True, True, 0)
        switch = Gtk.Switch()
        switch.connect("notify::active", self.startManagerActionEvent)
        switch.set_active(False)
        switch.set_halign(Gtk.Align.END)
        manager_selection.pack_end(switch, True, True, 0)
        manager_row.add(manager_selection)
        list_box.add(manager_row)

        clients_row = Gtk.ListBoxRow()
        client_info = Gtk.Box()
        self.num_clients_label_header = Gtk.Label("Number of clients connected: ", xalign=0)
        self.num_clients_label_footer = Gtk.Label()
        client_info.pack_start(self.num_clients_label_header, True, True, 0)
        client_info.pack_start(self.num_clients_label_footer, True, True, 0)
        clients_row.add(client_info)
        list_box.add(clients_row)

        workshops_row = Gtk.ListBoxRow()
        workshops_running = Gtk.Box()
        self.workshops_running_label = Gtk.Label("Workshops Running:", xalign=0)
        self.workshops_running_label.set_halign(Gtk.Align.CENTER)
        workshops_running.pack_start(self.workshops_running_label, True, True, 0)
        workshops_row.add(workshops_running)
        # list_box.add(workshops_row)
        self.bottom_box.pack_start(workshops_row, True, True, 0)
        self.bottom_box.show_all()

        self.add(self.outer_box)

    def startManagerActionEvent(self, button, active):
        command = ["python", MANAGER_BIN_DIRECTORY+"/instantiator.py"]
        if button.get_active():
            # Start the thread that executes the process and filters its output
            t = threading.Thread(target=self.watchProcess, args=(command,))
            t.start()
        else:
            # Destroy the thread
            self.destroy_process()

    def watchProcess(self, processPath):
        #Function for starting the process and capturing its stdout
        try:
            self.p = Popen(processPath, shell=False, stdout=PIPE, bufsize=1, cwd=MANAGER_BIN_DIRECTORY)
            with self.p.stdout:
                for line in iter(self.p.stdout.readline, b''):
                    if line.rstrip().lstrip() != "":
                        #print "line:", line
                        line = line.split(':')
                        if (line[0] == "Number of clients connected"):
                            self.num_clients = line[1]
                            self.num_clients_label_footer.set_label(str(self.num_clients))

                        elif (line[0] == "Workshops available") and (self.workshops_running != line[1]):
                            self.workshops_running = line[1]
                            self.setup_workshops_list(ast.literal_eval(line[1]))

            # wait for the subprocess to exit
            self.p.wait()
        except Exception as x:
            if self.p is None and self.p.poll() is not None:
                self.p.terminate()

    def destroy_process(self):
        #Sharing thread memory, so we have access to the process that it creates and watches
        #if the process is still running, terminate it
        if self.p != None and self.p.poll() == None:
            self.p.terminate()
        self.workshops_running = None
        self.bottom_box.remove(self.workshops_list_box)

    def setup_workshops_list(self, workshops):
        self.workshops_list_box = Gtk.ListBox()
        for workshop in workshops:
            self.workshops_list_box.add(WorkshopListBoxRow(workshop))
        self.bottom_box.pack_start(self.workshops_list_box, True, True, 0)
        self.workshops_list_box.show_all()
