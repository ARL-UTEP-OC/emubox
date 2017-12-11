#!/usr/bin/env bash
VENV_NAME=creator-container

pip install virtualenv
virtualenv $VENV_NAME

source ./$VENV_NAME/bin/activate
pip install lxml
pip install gi
cd bin
echo Type: python3 workshop-creator-gu.py to start the workshop-creator-gui

