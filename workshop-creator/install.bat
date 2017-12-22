REM Edit the following variables according to python installation
set PYTHONARCH=32
set PYTHONPACKAGES_PATH=Lib\site-packages\

REM name the container that will be created
set VENV_NAME=creator-container

pip install virtualenv
virtualenv "%VENV_NAME%"

IF %PYTHONARCH%==32 (
echo Processing using a 32-bit python27 installation
%VENV_NAME%\Scripts\activate & pip install lxml & pip install gi & xcopy python27-32bit-gtk3\* "%VENV_NAME%\%PYTHONPACKAGES_PATH%" /E /Y & %VENV_NAME%\Scripts\deactivate
REM Now create the file that will start the gui
echo REM the name of the container used during installation > start_gui.bat
echo set VENV_NAME=creator-container >> start_gui.bat
echo. >> start_gui.bat
echo REM activate the container and invoke the gui >> start_gui.bat
echo %VENV_NAME%\Scripts\activate ^& cd bin ^& python workshop_creator_gui.py >> start_gui.bat
echo Type: .\start_gui to start the workshop-creator-gui
) ELSE (
echo Processing using a 64-bit python27 installation
%VENV_NAME%\Scripts\activate & pip install lxml & pip install gi & xcopy python27-64bit-gtk3\* "%VENV_NAME%\%PYTHONPACKAGES_PATH%" /E /Y & %VENV_NAME%\Scripts\deactivate
REM Now create the file that will start the gui
echo REM the name of the container used during installation > start_gui.bat
echo set VENV_NAME=creator-container >> start_gui.bat
echo. >> start_gui.bat
echo REM activate the container and invoke the gui >> start_gui.bat
echo %VENV_NAME%\Scripts\activate ^& cd bin ^& python workshop_creator_gui.py >> start_gui.bat
echo Type: .\start_gui to start the workshop-creator-gui
)

