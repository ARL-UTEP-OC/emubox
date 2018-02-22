#!/usr/bin/env bash
VENV_NAME=creator-container

sudo apt-get install python-gi
sudo apt-get install python-pip

pip install virtualenv
virtualenv $VENV_NAME

source ./$VENV_NAME/bin/activate
pip install lxml
pip install vext
pip install vext.gi

#Generate the script 
echo "#!/usr/bin/env bash" > start_creator.sh
echo "#The name of the container used during installation" >> start_creator.sh
echo VENV_NAME=creator-container >> start_creator.sh
echo >> start_creator.sh
echo "#Activate the container and invoke the gui" >> start_creator.sh
echo source ./$VENV_NAME/bin/activate >> start_creator.sh
echo cd bin >> start_creator.sh
echo gsettings set com.canonical.Unity integrated-menus true >> start_creator.sh
echo python workshop_creator_gui.py >> start_creator.sh
echo gsettings set com.canonical.Unity integrated-menus false >> start_creator.sh

chmod 755 start_creator.sh
echo
echo
echo Type: ./start_creator.sh to start the workshop-creator-gui

