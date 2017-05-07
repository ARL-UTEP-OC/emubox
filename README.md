# The Emulation SandBox (EmuBox)

## System Requirements
* Python 2.x (tested with [v2.7](https://www.python.org/download/releases/2.7/))
* VirtualBox > 5.0 and matching VirtualBox API and Extensions Pack (tested with [v5.1.10](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1))
* Flask (tested with [v0.12](http://pypi.python.org/pypi/Flask/0.12))
* VirtualEnv (tested with [v15.1.0](https://virtualenv.pypa.io/en/stable/))

## Description
EmuBox uses the Flask python microframework as the web server gateway interface (WSGI) application.
This provides similar functionality as a fast server gateway interface (FCGI) application that allows 
multiple, concurrent connections to the web application.

Gevent is used to host the standalone flask WSGI container. This handles the concurrent WSGI behavior. It uses 
greenlet to provide high-level synchronous API  on top of libev event loop. 

EmuBox is composed of two main components: The Workshop Creator and the Workshop Manager.

### Workshop Creator
The Workshop Creator automates the creation of workshop units (sets of VMs that compose a cybersecurity scenario). This includes the cloning process.
During the cloning process, this component adjusts VRDP ports and internal
network adapter names so that each group is isolated and uniquely accessible by
participants.

### Workshop Manager

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

## Installation
### EmuBox has been tested on:
* Windows 7 (32 and 64-bit), Windows Server 2012 (64-bit)
* Kali Linux 2016.2 (32 and 64-bit)

### Windows
To install EmuBox, run `./install.bat`. This will install Flask and VirtualEnv required dependencies and will also create a virtualenv environment. An Internet connection is required for installation.

## Execution
First, you must invoke the workshop-manager virtualenv. In the directory where you installed EmuBox, type:
workshop-manager\Scripts\activate
cd workshop-manager

Next, execute EmuBox by typing:
python workshop-manager.py 

This will start a flask webserver and a backend monitor for virtualbox VMs.

## Workshop Units

The EmuBox uses the VirtualBox API to monitor and update groups of VMs (that compose a workshop unit). Users may connect to these units using remote desktop. When a user disconnects, EmuBox will restore all VMs in a unit from the most recent snapshot.
