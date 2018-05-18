#!/usr/bin/env bash
VENV_NAME=creator-container

apt-get install python-gi
apt-get install python-pip
apt-get install libgirepository1.0-dev

pip install virtualenv
virtualenv $VENV_NAME

source ./$VENV_NAME/bin/activate
#creator dependencies
pip install pygobject
pip install lxml
pip install vext
pip install vext.gi

#manager dependencies
pip install flask
pip install pyvbox
pip install gevent
pip install gevent-socketio
VBOX_INSTALL_PATH=$(which virtualbox)
VBOX_SDK_PATH=`pwd`/../workshop-manager/bin/VirtualBoxSDK-5.1.20-114628/sdk/
cd ../workshop-manager/bin/VirtualBoxSDK-5.1.20-114628/sdk/installer/
python vboxapisetup.py install
cd ../../../../../workshop-creator/

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
echo "#These variables are set based on their values when the install script is executed. Re-set values as needed." >> start_creator.sh
echo export VBOX_INSTALL_PATH=$VBOX_INSTALL_PATH >> start_creator.sh
echo export VBOX_SDK_PATH=$VBOX_SDK_PATH >> start_creator.sh
echo export VBOX_PROGRAM_PATH=$VBOX_PROGRAM_PATH >> start_creator.sh

chmod 755 start_creator.sh
echo
echo
echo Type: ./start_creator.sh to start the workshop-creator-gui

