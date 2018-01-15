REM name the container that will be created
set VENV_NAME=manager-container

REM Make sure path to pip is set correctly
pip install virtualenv
virtualenv %VENV_NAME%
%VENV_NAME%\Scripts\activate & pip install flask & pip install pyvbox & pip install gevent & pip install pypiwin32 & cd bin\VirtualBoxSDK-5.1.20-114628\sdk\installer\ & python vboxapisetup.py install & cd ..\..\..\ & echo Type: python instantiator.py to start EmuBox
