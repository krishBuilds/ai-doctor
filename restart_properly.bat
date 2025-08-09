@echo off
echo 🏥 AI Doctor - Proper WebSocket Server
echo.

echo Step 1: Stopping any existing server...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Installing Daphne (ASGI server)...
pip install daphne

echo Step 4: Running database migrations...
python manage.py migrate

echo Step 5: Starting server with WebSocket support...
echo.
echo 🌐 Access at: http://127.0.0.1:8080
echo ⏹️  Press Ctrl+C to stop
echo.

daphne -b 127.0.0.1 -p 8080 ai_doctor.asgi:application