#!/usr/bin/env bash
apt-get install python-pip
# Make sure path to pip is set correctly
pip install lxml & pip install gi
pip install virtualenv
virtualenv workshop-manager
source ./workshop-manager/bin/activate
pip install flask
pip install pyvbox
pip install gevent
VBOX_SDK_PATH=`pwd`/workshop-manager/VirtualBoxSDK-5.1.20-114628/sdk/
cd workshop-manager/VirtualBoxSDK-5.1.20-114628/sdk/installer/
python vboxapisetup.py install
cd ../../../
cp ../bin/workshop-manager/* . -rf
echo Type: python instantiator.py to start EmuBox
