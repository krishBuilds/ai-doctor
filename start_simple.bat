@echo off
echo 🏥 AI Doctor - Simple Start
echo.

echo Step 1: Stopping any existing servers...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Step 2: Checking environment...
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your OpenAI API key!
    echo OPENAI_API_KEY=sk-your-actual-key-here
    echo.
    pause
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Step 3: Activating environment and installing packages...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo Step 4: Running migrations...
python manage.py migrate --noinput

echo Step 5: Starting server...
echo.
echo 🌐 Access at: http://127.0.0.1:8080
echo 💡 Note: WebSockets disabled, using HTTP chat
echo ⏹️  Press Ctrl+C to stop
echo.

python manage.py runserver 127.0.0.1:8080