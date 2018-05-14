import threading
import gi; gi.require_version('Gtk', '3.0')
import workshop_creator_gui_resources.gui_constants as gui_constants
from subprocess import Popen, PIPE
from gi.repository import Gtk


MANAGER_INSTANTIATOR_DIRECTORY = gui_constants.MANAGER_INSTANTIATOR_DIRECTORY


class ManagerBox(Gtk.Box):

    def __init__(self, *args, **kwargs):
        super(ManagerBox, self).__init__(*args, **kwargs)

        self.num_clients = 0
        self.workshops_running = []

        switch = Gtk.Switch()
        switch.connect("notify::active", self.startManagerActionEvent)
        switch.set_active(False)

        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        manager_row = Gtk.ListBoxRow()
        manager_selection = Gtk.Box(spacing=500)
        manager_label = Gtk.Label("Manager", xalign=0)
        manager_selection.pack_start(manager_label, True, True, 0)
        manager_selection.pack_start(switch, True, True, 0)
        manager_row.add(manager_selection)
        list_box.add(manager_row)

        clients_row = Gtk.ListBoxRow()
        client_info = Gtk.Box(spacing=500)
        num_clients_label_header = Gtk.Label("Number of clients connected: ", xalign=0)
        num_clients_label_footer = Gtk.Label(str(self.num_clients))
        client_info.pack_start(num_clients_label_header, True, True, 0)
        client_info.pack_start(num_clients_label_footer, True, True, 0)
        clients_row.add(client_info)
        list_box.add(clients_row)

        workshops_row = Gtk.ListBoxRow()
        workshops_running = Gtk.Box(spacing=500)
        workshops_running_header = Gtk.Label("Workshops Running:", xalign=0)
        workshops_running_footer = Gtk.Label(self.workshops_running)
        workshops_running.pack_start(workshops_running_header, True, True, 0)
        workshops_running.pack_start(workshops_running_footer, True, True, 0)
        workshops_row.add(workshops_running)
        list_box.add(workshops_row)

        self.add(list_box)

        self.p = None
        self.curr_out_buff_pos = 0
        self.curr_read_buff_pos = 0
        self.curr_out_buff = []

    def startManagerActionEvent(self, button, active):
        command = ["python", MANAGER_INSTANTIATOR_DIRECTORY]
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
            self.p = Popen(processPath, shell=False, stdout=PIPE, bufsize=1)
            with self.p.stdout:
                for line in iter(self.p.stdout.readline, b''):
                    if line.rstrip().lstrip() != "":
                        print line
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
