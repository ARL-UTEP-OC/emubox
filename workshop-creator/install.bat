REM Edit the following variables according to python installation
set PYTHONARCH=32
set PYTHONPACKAGES_PATH=Lib\site-packages\

REM name the container that will be created
set VENV_NAME=creator-container

pip install virtualenv
virtualenv "%VENV_NAME%"

IF %PYTHONARCH%==32 (
echo Processing using a 32-bit python27 installation
%VENV_NAME%\Scripts\activate & pip install lxml & pip install gi & xcopy python27-32bit-gtk3\* "%VENV_NAME%\%PYTHONPACKAGES_PATH%" /E /Y & cd bin & echo Type: python workshop-creator-gu.py to start the workshop-creator-gui
) ELSE (
echo Processing using a 64-bit python27 installation
%VENV_NAME%\Scripts\activate & pip install lxml & pip install gi & xcopy python27-64bit-gtk3\* "%VENV_NAME%\%PYTHONPACKAGES_PATH%" /E /Y & cd bin & echo Type: python workshop-creator-gu.py to start the workshop-creator-gui
)