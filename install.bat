REM Make sure path to pip is set correctly
pip install virtualenv
virtualenv workshop-manager
workshop-manager\Scripts\activate & pip install flask & pip install pyvbox & pip install gevent & pip install pypiwin32 & cd workshop-manager\VirtualBoxSDK-5.1.20-114628\sdk\installer\ & python vboxapisetup.py install & cd ..\..\..\ & copy ..\bin\workshop-manager\workshop-manager.py . & echo Type: python workshop-manager.py to start EmuBox
