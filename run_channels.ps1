# AI Doctor - PowerShell Channels/WebSocket Server Launcher
# Run Django with ASGI for WebSocket support

param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8080
)

Write-Host "🏥 Starting AI Doctor with WebSocket Support (Channels)" -ForegroundColor Green
Write-Host "Host: $Host" -ForegroundColor Yellow
Write-Host "Port: $Port" -ForegroundColor Yellow

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "🔧 Please edit .env file and add your OpenAI API key" -ForegroundColor Cyan
    notepad .env
    pause
}

# Check/create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "🔧 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install/update requirements
Write-Host "📦 Installing requirements..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q daphne  # ASGI server for channels

# Run migrations
Write-Host "🗃️  Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
Write-Host "📁 Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Check OpenAI API key
$envContent = Get-Content ".env" -Raw
if ($envContent -match "OPENAI_API_KEY=your_openai_api_key_here") {
    Write-Host "⚠️  WARNING: OpenAI API key not configured!" -ForegroundColor Red
    Write-Host "Edit .env file and set: OPENAI_API_KEY=sk-your-actual-key" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting Django Channels server with WebSocket support..." -ForegroundColor Green
Write-Host "🌐 Access at: http://${Host}:${Port}" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Run with Daphne (ASGI server)
daphne -b $Host -p $Port ai_doctor.asgi:application