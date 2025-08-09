# AI Doctor - PowerShell Server Launcher
# Run the Django application on custom host and port

param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8080,
    [string]$Environment = "development"
)

Write-Host "🏥 Starting AI Doctor Application" -ForegroundColor Green
Write-Host "Host: $Host" -ForegroundColor Yellow
Write-Host "Port: $Port" -ForegroundColor Yellow
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env file created from .env.example" -ForegroundColor Green
        Write-Host "🔧 Please edit .env file and add your OpenAI API key" -ForegroundColor Cyan
        
        # Open .env file for editing
        if (Get-Command notepad -ErrorAction SilentlyContinue) {
            Start-Process notepad ".env"
        }
        
        Write-Host "Press any key to continue after editing .env file..."
        $null = $Host.UI.ReadLine()
    } else {
        Write-Host "❌ .env.example not found! Please create .env file manually." -ForegroundColor Red
        exit 1
    }
}

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "🔧 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment. Make sure Python is installed." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment." -ForegroundColor Red
    exit 1
}

# Install/update requirements
Write-Host "📦 Installing/updating Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some packages failed to install. Continuing anyway..." -ForegroundColor Yellow
}

# Run database migrations
Write-Host "🗃️  Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Database migrations had issues. Continuing anyway..." -ForegroundColor Yellow
}

# Collect static files
Write-Host "📁 Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Check if OpenAI API key is set
Write-Host "🔑 Checking OpenAI configuration..." -ForegroundColor Yellow
$envContent = Get-Content ".env" -Raw
if ($envContent -match "OPENAI_API_KEY=your_openai_api_key_here" -or $envContent -notmatch "OPENAI_API_KEY=sk-") {
    Write-Host "⚠️  OpenAI API key not configured properly!" -ForegroundColor Red
    Write-Host "Please edit .env file and set your OpenAI API key:" -ForegroundColor Yellow
    Write-Host "OPENAI_API_KEY=sk-your-actual-key-here" -ForegroundColor Cyan
    
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
} else {
    Write-Host "✅ OpenAI API key configured" -ForegroundColor Green
}

# Start Redis (optional - comment out if you don't have Redis)
Write-Host "🔴 Checking Redis server..." -ForegroundColor Yellow
$redisRunning = Get-Process redis-server -ErrorAction SilentlyContinue
if (!$redisRunning) {
    Write-Host "⚠️  Redis server not running. Chat features may be limited." -ForegroundColor Yellow
    Write-Host "💡 To install Redis on Windows:" -ForegroundColor Cyan
    Write-Host "   1. Download Redis from https://github.com/tporadowski/redis/releases" -ForegroundColor Cyan
    Write-Host "   2. Or use WSL: wsl --install then sudo apt install redis-server" -ForegroundColor Cyan
}

# Update ALLOWED_HOSTS in settings if needed
if ($Host -ne "127.0.0.1" -and $Host -ne "localhost") {
    Write-Host "🔧 Updating ALLOWED_HOSTS for custom host..." -ForegroundColor Yellow
    # This is handled by environment variables in settings.py
}

Write-Host "🚀 Starting Django development server..." -ForegroundColor Green
Write-Host "🌐 Access your AI Doctor at: http://${Host}:${Port}" -ForegroundColor Cyan
Write-Host "📱 For mobile access, use your actual IP address instead of 127.0.0.1" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Set environment variables
$env:DJANGO_HOST = $Host
$env:DJANGO_PORT = $Port
$env:DJANGO_DEBUG = if ($Environment -eq "production") { "False" } else { "True" }

# Start the Django server
python manage.py runserver "${Host}:${Port}"

Write-Host "👋 AI Doctor server stopped." -ForegroundColor Yellow