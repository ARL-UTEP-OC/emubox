#!/usr/bin/env bash
VENV_NAME=manager-container

apt-get install python-pip
# Make sure path to pip is set correctly
pip install lxml & pip install gi
pip install virtualenv
virtualenv $VENV_NAME
source ./$VENV_NAME/bin/activate
pip install flask
pip install pyvbox
pip install gevent
VBOX_SDK_PATH=`pwd`/bin/VirtualBoxSDK-5.1.20-114628/sdk/
cd bin/VirtualBoxSDK-5.1.20-114628/sdk/installer/
python vboxapisetup.py install
cd ../../../
echo Type: python instantiator.py to start EmuBox
