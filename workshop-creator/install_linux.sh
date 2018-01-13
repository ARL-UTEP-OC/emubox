#!/usr/bin/env bash
VENV_NAME=creator-container

pip install virtualenv
virtualenv $VENV_NAME

source ./$VENV_NAME/bin/activate
pip install lxml
pip install gi

#Generate the script 
echo "#!/usr/bin/env bash" > start_gui.sh
echo "#The name of the container used during installation" >> start_gui.sh
echo VENV_NAME=creator-container >> start_gui.sh
echo >> start_gui.sh
echo "#Activate the container and invoke the gui" >> start_gui.sh
echo source ./$VENV_NAME/bin/activate >> start_gui.sh
echo cd bin >> start_gui.sh
echo python3 workshop_creator_gui.py >> start_gui.sh

chmod 755 start_gui.sh
echo
echo
echo Type: ./start_gui.sh to start the workshop-creator-gui

