import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MainWindow(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, title="Workshop Creator GUI")

#class MainWidget

def main():
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__": main()
