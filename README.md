# AI Assistant Pro

A professional AI assistant application with voice support and 3D avatar integration using OpenAI APIs.

## Features

- 🤖 **Professional AI Assistant** - Generic AI assistant powered by OpenAI GPT-4o mini
- 🎭 **3D Avatar with Lip Sync** - Professional avatar with realistic lip synchronization
- 🎤 **Voice Support** - Speech-to-text and text-to-speech capabilities
- 💬 **Real-time Chat** - WebSocket-based real-time messaging
- 🌐 **Modern Web Interface** - Clean, professional UI design

## Tech Stack

- **Backend**: Django with Channels (WebSocket support)
- **Frontend**: Vanilla JavaScript with modern ES6+ features
- **AI Integration**: OpenAI GPT-4o mini, TTS-1, Whisper-1
- **Avatar System**: Canvas-based professional avatar with Ready Player Me fallback
- **Real-time Communication**: WebSocket with Daphne ASGI server

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/BuildingKrishan/ai-doctor.git
   cd ai-doctor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   - The `.env` file contains your OpenAI API key:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   OPENAI_API_KEY=your-openai-api-key-here
   ```

4. **Database Setup**
   ```bash
   python manage.py migrate
   ```

5. **Start the application**
   ```bash
   daphne -b 127.0.0.1 -p 8080 ai_doctor.asgi:application
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:8080`

## Usage

1. **Chat Interface**: Type messages in the chat interface
2. **Voice Input**: Use the microphone button for voice input
3. **Avatar Interaction**: Watch the professional avatar respond with lip sync
4. **Export History**: Export chat history for reference

### Features

- **Professional Avatar**: Generic professional assistant (no medical-specific branding)
- **Real-time Responses**: Instant AI responses powered by OpenAI GPT-4o mini
- **Voice Support**: Speech-to-text and text-to-speech capabilities
- **Modern Interface**: Clean, professional design
- **WebSocket Communication**: Real-time messaging with no page refreshes

### API Configuration

The application uses OpenAI APIs with cost-optimized settings:
- **Chat Model**: GPT-4o mini (cheapest GPT-4 class model)
- **TTS Model**: TTS-1 (standard quality, cost-effective)
- **STT Model**: Whisper-1 (only available Whisper model)

## Development

### Project Structure

```
ai-doctor/
├── ai_doctor/          # Django project settings
├── avatar/             # Avatar models and logic
├── voice/              # Voice processing
├── chat/               # Chat and WebSocket handling
├── animation/          # Gesture and animation system
├── static/             # Frontend assets (JS, CSS)
├── templates/          # HTML templates
└── media/              # Generated audio files
```

### Key Components

- **ChatConsumer**: WebSocket handler for real-time communication
- **AvatarManager**: Three.js avatar rendering and animation
- **VoiceManager**: Speech recognition and TTS playback
- **ChatService**: LLM integration with medical prompts
- **AnimationService**: Gesture analysis and lip sync

### Adding Custom Gestures

1. Define gesture in `animation/services.py`
2. Add animation logic in `static/js/avatar.js`
3. Update keyword mapping for auto-triggering

### Extending Medical Context

1. Add fields to `MedicalContext` model
2. Update frontend form in `templates/index.html`
3. Modify prompt building in `ChatService`

## API Endpoints

- `ws://localhost:8000/ws/chat/<session_id>/` - Chat WebSocket
- `ws://localhost:8000/ws/avatar/<session_id>/` - Avatar WebSocket
- `/admin/` - Django admin interface

## Cost Optimization

This prototype uses free/low-cost services:

- **edge-tts**: Free Microsoft TTS (no API key needed)
- **Web Speech API**: Free browser-based STT
- **OpenAI GPT-3.5**: ~$0.002 per conversation
- **Claude Haiku**: ~$0.001 per conversation

## Deployment

### Production Considerations

1. **Set DEBUG=False** in production
2. **Use PostgreSQL** instead of SQLite
3. **Configure CORS** for your domain
4. **Use AWS S3** for media files
5. **Add SSL/HTTPS** for WebSocket connections
6. **Scale with load balancer** and multiple workers

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**: Make sure Redis is running
2. **Microphone Not Working**: Enable browser microphone permissions
3. **Avatar Not Loading**: Check Three.js console errors
4. **API Errors**: Verify API keys in `.env`

### Debug Mode

Set `DEBUG=True` and check browser console for detailed errors.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with details

---

Built with ❤️ for healthcare innovation