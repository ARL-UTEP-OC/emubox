# The Emulation SandBox (EmuBox)

### Description
EmuBox uses the Flask python microframework as the web server gateway interface (WSGI) application.
This provides similar functionality as a fast common gateway interface (FCGI) application that allows 
multiple, concurrent connections to the web application.

Gevent is used to host the standalone flask WSGI container. This handles the concurrent WSGI behavior. It uses 
greenlet to provide high-level synchronous API on top of libev event loop. 

EmuBox is composed of two main components: The Workshop Creator and the Workshop Manager.

#### Workshop Creator
The Workshop Creator automates the creation of workshop units (sets of VMs that compose a cybersecurity scenario). This includes the cloning process.
During the cloning process, this component adjusts VRDP ports and internal
network adapter names so that each group is isolated and uniquely accessible by
participants.

#### Workshop Creator GUI
The Workshop Creator GUI provides a graphical interface to design workshop units and modify their parameters.  The user can then run the Workshop Creator script via the interface, eliminating the need to set command line parameters manually.

To run the Workshop Creator GUI, navigate to the container directory in a command line and enter the command "python workshop_creator_gui.py".

#### Workshop Manager

The Workshop Manager component of EmuBox is a multi-threaded process that
monitors VRDP connections for each workshop unit. It also contains a web service
with a simple front-end that is implemented using the Flask micro web development
framework. When participants navigate to the front-end they are shown the
VRDP-enabled workshop units (those that are available and not currently in use).
The front-end also provides participants with a unique connection string (IP
address and VRDP port pair) to use in a remote desktop client, such as MS-RDP on
Windows, Mac OS, iOS, and rdesktop on Linux.

When a participant connects to a a unit, it becomes unavailable and will no
longer be shown in the web interface. After a participant disconnects from the
unit, the system will automatically restore the associated VMs from snapshot
and make it available once again.

#### Workshop Units

The EmuBox uses the VirtualBox API to monitor and update groups of VMs (that compose a workshop unit). Users may connect to these units using remote desktop. When a user disconnects, EmuBox will restore all VMs in a unit from the most recent snapshot.

## Installation
#### EmuBox has been tested on:
* Windows 7 (32 and 64-bit), Windows Server 2012 (64-bit)
* Ubuntu 16.04 LTE (64-bit)

#### Requirements
##### You must install these manually:
* Python 2.x (tested with [v2.7](https://www.python.org/download/releases/2.7/))
* VirtualBox > 5.0 and matching VirtualBox API and Extensions Pack (tested with [v5.1.10](https://www.virtualbox.org/wiki/Downloads))
* PyGI (requires v3.10.2, on Windows, tested using [this Windows Installer](https://sourceforge.net/projects/pygobjectwin32/files/pygi-aio-3.10.2-win32_rev18-setup.exe/download)
    
    Install both:
    * gobject-introspection
    * adg

##### These are automatically installed with the included install script
* VirtualEnv (tested with [v15.1.0](https://virtualenv.pypa.io/en/stable/) )
* LXML (tested with [v4.0.0](http://lxml.de/changes-4.0.0.html) )
* Flask (tested with [v0.12](http://pypi.python.org/pypi/Flask/0.12) )

#### Windows
In the directory where you extracted EmuBox:
```
cd workshop-manager
./install.bat
```

#### Linux
In the directory where you extracted EmuBox:
```
sudo -s
cd workshop-manager
```
Set the following environment variables

* VBOX_INSTALL_PATH
* VBOX_SDK_PATH
* VBOX_PROGRAM_PATH

For example, 
```
export VBOX_INSTALL_PATH=$(which virtualbox)
export VBOX_SDK_PATH=`pwd`/bin/VirtualBoxSDK-5.1.20-114628/sdk/
export VBOX_PROGRAM_PATH=/usr/lib/virtualbox/
```
Now run the installer and start emubox
```
source ./install.sh
./start_manager.sh
```

## Execution

This will start a flask webserver and a backend monitor for virtualbox VMs.
#### Windows
In the directory where you installed EmuBox, type:
```
cd workshop-manager
./start_manager.sh
```

#### Linux
In the directory where you installed EmuBox, type:
```
sudo -s
cd workshop-manager
./start_manager.sh
```
NOTE: You must run VirtualBox as a sudo user in order for remote display, and hence, emubox, to work correctly.


### Live Disc
A live disc containing preinstalled EmuBox is available [here](https://goo.gl/xmsMik).
The following are the steps for running EmuBox on the live disc.
#### DHCP Service Configuration (Optional)
Start DHCP Server
1. Modify the following files to assign the dhcp server interface and network range (enp0s3 is the default interface):
/etc/dhcp/dhcpd.conf
/etc/default/isc-dhcp-server
2. Modify the following file to set a static IP address to the interface serving DHCP:
/etc/network/interfaces
3. Start the dhcp service:
service isc-dhcp-server start

#### EmuBox Manager
To Start EmuBox:
1. Open a terminal window and execute the following commands:
```
sudo -s
cd /root/emubox/workshop-manager
./start_manager.sh
```
