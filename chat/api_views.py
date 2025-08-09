"""
HTTP API Views for Chat (when WebSocket is not available)
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from asgiref.sync import sync_to_async
import asyncio

from .services import ChatService, TTSService

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """HTTP API endpoint for chat when WebSocket is not available"""
    
    def __init__(self):
        super().__init__()
        self.chat_service = ChatService()
        self.tts_service = TTSService()
    
    async def post(self, request):
        """Handle chat message via HTTP POST"""
        try:
            # Parse request data
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', 'default')
            
            if not message:
                return JsonResponse({
                    'success': False,
                    'error': 'Message cannot be empty'
                })
            
            logger.info(f"HTTP Chat - Session: {session_id}, Message: {message[:100]}")
            
            # Get AI response
            response_data = await self.chat_service.get_medical_response(message, session_id)
            
            # Handle different response formats
            if isinstance(response_data, dict):
                ai_message = response_data.get('message', str(response_data))
                gesture = response_data.get('gesture', 'professional')
                mood = response_data.get('mood', 'professional')
                urgency = response_data.get('urgency', 'low')
            else:
                ai_message = str(response_data)
                gesture = 'professional'
                mood = 'professional'
                urgency = 'low'
            
            # Generate TTS audio if enabled
            audio_url = None
            try:
                if hasattr(self.tts_service, 'text_to_speech'):
                    audio_url = await self.tts_service.text_to_speech(ai_message, session_id)
            except Exception as tts_error:
                logger.warning(f"TTS generation failed: {tts_error}")
            
            # Return structured response
            return JsonResponse({
                'success': True,
                'message': ai_message,
                'gesture': gesture,
                'mood': mood,
                'urgency': urgency,
                'audio_url': audio_url,
                'session_id': session_id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Chat API error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error. Please try again.'
            })
    
    def dispatch(self, request, *args, **kwargs):
        """Override to handle async views in Django"""
        if request.method.upper() == 'POST':
            # Run async post method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.post(request))
            finally:
                loop.close()
        else:
            return JsonResponse({
                'success': False,
                'error': 'Only POST method allowed'
            })


@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'AI Doctor Chat API',
        'websockets_available': False  # This indicates HTTP fallback mode
    })


@require_http_methods(["POST"])
@csrf_exempt
def tts_api(request):
    """Text-to-Speech API endpoint"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        session_id = data.get('session_id', 'default')
        voice = data.get('voice')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text cannot be empty'
            })
        
        # Generate TTS
        tts_service = TTSService()
        
        async def generate_tts():
            return await tts_service.text_to_speech(text, session_id, voice)
        
        # Run async TTS
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            audio_url = loop.run_until_complete(generate_tts())
        finally:
            loop.close()
        
        if audio_url:
            return JsonResponse({
                'success': True,
                'audio_url': audio_url
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'TTS generation failed'
            })
            
    except Exception as e:
        logger.error(f"TTS API error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'TTS service error'
        })