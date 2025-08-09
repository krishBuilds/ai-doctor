# AI Doctor Avatar - Quick Start Guide

## 🚀 Your Server is Running!

The AI Doctor Avatar prototype is now running at:
**http://localhost:8000**

## 📱 How to Access

1. Open your web browser
2. Navigate to: `http://localhost:8000`
3. You should see the AI Doctor Avatar interface

## 🎮 How to Use

### Basic Chat
- Type your medical questions in the chat box
- Click "Send" or press Enter
- The AI doctor will respond with medical guidance

### Voice Input
- Click the microphone button (🎤) 
- Or press **Spacebar** to toggle voice input
- Speak your question clearly
- The system will transcribe and respond

### Avatar Interactions
- Watch the 3D avatar perform gestures
- Click the gesture button (👋) for manual animations
- The avatar responds contextually to conversations

### Medical Context
- Fill in patient information in the right panel:
  - Age
  - Current symptoms  
  - Medical history
- This helps provide more relevant responses

## 🛠️ Features Available

✅ **3D Avatar Rendering** - Three.js with fallback geometry  
✅ **Voice Recognition** - Web Speech API (Chrome/Edge)  
✅ **Text-to-Speech** - Free edge-tts engine  
✅ **Medical AI Chat** - Fallback responses (add API keys for full AI)  
✅ **Gesture System** - Context-aware animations  
✅ **Responsive UI** - Works on desktop and mobile  

## 🔧 Optional: Add AI API Keys

To enable full AI responses, edit `.env` file:

```bash
# Add your API key (get from OpenAI or Anthropic)
OPENAI_API_KEY=your-actual-api-key-here
# OR
ANTHROPIC_API_KEY=your-actual-api-key-here
```

Then restart the server.

## 📞 Troubleshooting

**Can't access localhost:8000?**
- Make sure the server is running (see console output)
- Try: `http://127.0.0.1:8000`
- Check Windows firewall settings

**Voice not working?**
- Use Chrome or Edge browser
- Allow microphone permissions
- Ensure microphone is working

**Avatar not loading?**
- Check browser console for errors
- Try refreshing the page
- Fallback avatar should still appear

## 🎯 Development Commands

```bash
# Start server
python start_server.py

# Or manually
python manage.py runserver 0.0.0.0:8000

# Run with Docker
docker-compose up --build
```

## 📈 Next Steps

1. **Add your API keys** for full AI responses
2. **Upload custom VRM avatar** to `static/models/doctor_avatar.vrm`
3. **Customize medical prompts** in `chat/services.py`
4. **Add more gestures** in `animation/services.py`

---

🏥 **AI Doctor Avatar is ready for medical consultations!**