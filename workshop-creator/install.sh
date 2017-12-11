#!/usr/bin/env bash
VENV_NAME=creator-container

pip install virtualenv
virtualenv $VENV_NAME

source ./$VENV_NAME/bin/activate
pip install lxml
pip install gi
apt-get install python-gobject
apt-get install libgtk-3-dev
cd bin
echo Type: python workshop-creator-gu.py to start the workshop-creator-gui

