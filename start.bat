@echo off
echo Starting AI Doctor Application...
echo.

REM Default settings
set HOST=127.0.0.1
set PORT=8080

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo Please edit .env file and add your OpenAI API key!
    echo Opening .env file for editing...
    notepad .env
    pause
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Start server
echo.
echo Starting AI Doctor server...
echo Access at: http://%HOST%:%PORT%
echo Press Ctrl+C to stop
echo.
python manage.py runserver %HOST%:%PORT%

pause