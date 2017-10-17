REM Make sure path to pip is set correctly
pip install lxml & pip install gi
pip install virtualenv
virtualenv workshop-manager
workshop-manager\Scripts\activate & pip install flask & pip install pyvbox & pip install gevent & pip install pypiwin32 & cd workshop-manager\VirtualBoxSDK-5.1.20-114628\sdk\installer\ & python vboxapisetup.py install & cd ..\..\..\ & xcopy ..\bin\workshop-manager . /E /Y & echo Type: python instantiator.py to start EmuBox
