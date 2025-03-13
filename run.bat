@echo off
setlocal

set VENV_DIR=venv

REM Check if virtual environment exists, create if it doesn't
if not exist %VENV_DIR%\ (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo Failed to create virtual environment. Is Python 3 installed?
        exit /b 1
    )
    echo Virtual environment created successfully.
)

REM Activate virtual environment
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Install or update requirements
echo Installing/updating requirements...

REM First try: Standard installation
pip install -r requirements.txt
if errorlevel 1 (
    echo Standard installation failed. Trying alternative approaches...
    
    REM Second try: Install lxml separately with binary wheel
    echo Attempting to install lxml as binary wheel...
    pip install --only-binary :all: lxml
    
    REM If that fails, provide guidance
    if errorlevel 1 (
        echo.
        echo Binary wheel installation failed.
        echo.
        echo For Windows users:
        echo 1. Try installing lxml using a precompiled wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
        echo 2. Download the appropriate .whl file for your Python version
        echo 3. Install it with: pip install C:\path\to\downloaded\lxml_file.whl
        echo 4. Then run this script again
        echo.
        call deactivate
        exit /b 1
    )
    
    REM Install remaining requirements without lxml
    echo Installing remaining requirements...
    
    REM Create temporary file without lxml
    echo Creating temporary requirements file without lxml...
    findstr /v "lxml" requirements.txt > requirements_no_lxml.txt
    
    REM Install requirements without lxml
    pip install -r requirements_no_lxml.txt
    
    REM Check if installation was successful
    if errorlevel 1 (
        echo Failed to install requirements after multiple attempts.
        del requirements_no_lxml.txt
        call deactivate
        exit /b 1
    )
    
    REM Clean up
    del requirements_no_lxml.txt
)

REM Run the script
echo Running Upwork Job Search Alerts...
python upwork-job-search-alerts.py

REM Deactivate virtual environment when the script exits
call deactivate

endlocal