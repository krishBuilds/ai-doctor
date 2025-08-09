# 🏥 AI Doctor - Setup & Run Guide

## 🚀 Quick Start Commands

### **For PowerShell (Run this):**

```powershell
# Stop any existing server first (Ctrl+C)
# Then run this command in PowerShell:

cd "C:\Users\krish\source\repos\ai-doctor" ; .\venv\Scripts\Activate.ps1 ; pip install daphne ; daphne -b 127.0.0.1 -p 8080 ai_doctor.asgi:application
```

### **Alternative: Run with WebSocket support:**

```powershell
cd "C:\Users\krish\source\repos\ai-doctor" ; powershell -ExecutionPolicy Bypass -File .\run_channels.ps1 -Host "127.0.0.1" -Port 8080
```

## 🔧 First Time Setup

### 1. **Create .env file:**
```powershell
cd "C:\Users\krish\source\repos\ai-doctor"
copy .env.example .env
notepad .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. **Install Dependencies:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install daphne
```

### 3. **Setup Database:**
```powershell
python manage.py migrate
```

## 🎯 Running the Server

### **Option 1: Daphne (WebSocket Support) - RECOMMENDED**
```powershell
# This supports WebSockets for chat
daphne -b 127.0.0.1 -p 8080 ai_doctor.asgi:application
```

### **Option 2: Django Development Server (No WebSocket)**
```powershell
# Basic server without chat support
python manage.py runserver 127.0.0.1:8080
```

## 🌐 Access URLs

- **Local:** http://127.0.0.1:8080
- **Network:** http://your-ip:8080

## ✅ Features Working

- ✅ GPT-4o Mini integration
- ✅ OpenAI Text-to-Speech
- ✅ Medical consultation chat
- ✅ 3D Avatar (fallback mode)
- ✅ Voice input/output
- ✅ Gesture system

## 🔴 Troubleshooting

### **WebSocket Error (404 on /ws/chat/)**
Run with Daphne instead of manage.py runserver:
```powershell
daphne -b 127.0.0.1 -p 8080 ai_doctor.asgi:application
```

### **Avatar Shows as Simple Shape**
This is the fallback avatar. The Ready Player Me avatar requires:
- Good internet connection for loading 3D model
- WebGL support in browser

### **No Chat Response**
1. Check .env file has valid OpenAI API key
2. Check console for errors (F12 in browser)
3. Ensure running with Daphne (not runserver)

### **Install Redis (Optional - for better performance)**
```powershell
# Download from: https://github.com/tporadowski/redis/releases
# Or use WSL:
wsl --install
wsl
sudo apt update && sudo apt install redis-server
redis-server
```

## 📝 Test Your Setup

1. Open browser to http://127.0.0.1:8080
2. You should see the medical interface
3. Type "Hello" in chat
4. If working, you'll get a response from Dr. AI

## 🔑 OpenAI API Key

Get your key from: https://platform.openai.com/api-keys

**Pricing (GPT-4o Mini):**
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- TTS: $0.015 / 1K characters

Very affordable for testing!