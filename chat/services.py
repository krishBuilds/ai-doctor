import os
import asyncio
import json
import logging
from django.conf import settings
from .models import Session, MedicalContext

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

# Simple OpenAI service import
def get_simple_openai_service():
    try:
        from .simple_openai_service import simple_openai_service
        return simple_openai_service
    except Exception as e:
        logger.warning(f"Simple OpenAI service not available: {e}")
        return None


class ChatService:
    def __init__(self):
        self.openai_service = get_simple_openai_service()
        logger.info("✅ ChatService initialized with simple OpenAI integration")

    async def get_medical_response(self, user_message, session_id):
        """Get chat response using simple OpenAI service"""
        try:
            # Get conversation history 
            conversation_history = await self.get_conversation_history(session_id)
            
            # Use simple OpenAI service
            if settings.ENABLE_OPENAI_INTEGRATION and self.openai_service:
                response_data = await self.openai_service.get_chat_response(
                    user_message=user_message,
                    conversation_history=conversation_history
                )
                
                logger.info(f"✅ Got response from OpenAI: {response_data['type']}")
                
                # Return response for frontend
                return {
                    'message': response_data['response'],
                    'gesture': response_data.get('gesture', 'professional'),
                    'mood': response_data.get('mood', 'professional'),
                    'urgency': response_data.get('urgency', 'low'),
                    'type': response_data.get('type', 'ai_response')
                }
            else:
                # Fallback response
                return await self.get_fallback_response(user_message)
                
        except Exception as e:
            logger.error(f"❌ Error getting chat response: {e}")
            return {
                'message': "I apologize, I'm experiencing technical difficulties. Please try again in a moment.",
                'gesture': 'professional',
                'mood': 'professional',
                'urgency': 'low',
                'type': 'error'
            }

    async def get_conversation_history(self, session_id, limit=5):
        """Get recent conversation history"""
        try:
            from channels.db import database_sync_to_async
            
            @database_sync_to_async
            def get_history():
                # This would get from your chat history model
                # For now, return empty list
                return []
            
            return await get_history()
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    async def get_medical_context_dict(self, session_id):
        """Get medical context as dictionary"""
        try:
            from channels.db import database_sync_to_async
            
            @database_sync_to_async
            def get_context():
                try:
                    session = Session.objects.get(id=session_id)
                    context = getattr(session, 'medical_context', None)
                    if context:
                        return {
                            'age': getattr(context, 'patient_age', None),
                            'symptoms': getattr(context, 'symptoms', None),
                            'medical_history': getattr(context, 'medical_history', None),
                            'urgency_level': getattr(context, 'urgency_level', 'routine')
                        }
                    return {}
                except Session.DoesNotExist:
                    return {}
            
            return await get_context()
            
        except Exception as e:
            logger.error(f"Error getting medical context: {e}")
            return {}

    async def get_anthropic_response(self, user_message, system_prompt):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
        )
        return response.content[0].text

    async def get_fallback_response(self, user_message):
        responses = {
            "hello": "Hello! I'm Dr. AI, your virtual medical assistant. How can I help you today?",
            "pain": "I understand you're experiencing pain. Can you describe where the pain is located and how severe it is on a scale of 1-10?",
            "fever": "A fever can indicate various conditions. Have you taken your temperature? Any other symptoms like headache or body aches?",
            "appointment": "I can help provide general health information, but for specific medical concerns, I recommend scheduling an appointment with your healthcare provider.",
        }
        
        user_lower = user_message.lower()
        for keyword, response in responses.items():
            if keyword in user_lower:
                return response
        
        return "I'm here to help with your health questions. Could you please provide more details about your symptoms or concerns?"

    def build_medical_system_prompt(self, medical_context):
        return f"""You are Dr. AI, a compassionate and knowledgeable virtual medical assistant. 
        
        Guidelines:
        - Provide helpful, accurate health information
        - Always recommend consulting healthcare professionals for serious concerns  
        - Be empathetic and understanding
        - Ask clarifying questions when needed
        - Never provide specific diagnoses or prescriptions
        - Focus on general wellness and health education
        
        Patient Context:
        {medical_context if medical_context else 'No specific medical context available.'}
        
        Respond in a warm, professional manner as a caring doctor would."""

    async def get_medical_context(self, session_id):
        try:
            from django.db import IntegrityError
            from channels.db import database_sync_to_async
            
            @database_sync_to_async
            def get_context():
                try:
                    session = Session.objects.get(id=session_id)
                    context = getattr(session, 'medical_context', None)
                    if context:
                        return f"Age: {context.patient_age}, Symptoms: {context.symptoms}, History: {context.medical_history}"
                    return "No medical context available"
                except Session.DoesNotExist:
                    return "Session not found"
            
            return await get_context()
        except Exception:
            return "No medical context available"


class TTSService:
    def __init__(self):
        self.openai_service = get_simple_openai_service()
        logger.info("✅ TTSService initialized with simple OpenAI integration")

    async def text_to_speech(self, text, session_id=None, voice=None):
        """Generate speech using simple OpenAI TTS"""
        try:
            import uuid
            from django.conf import settings
            
            # Handle both string and dict inputs
            if isinstance(text, dict):
                text_content = text.get('response', '') or text.get('message', '') or str(text)
            else:
                text_content = str(text)
            
            if not text_content.strip():
                logger.warning("Empty text provided for TTS")
                return None
            
            # Try OpenAI TTS if available
            if (settings.ENABLE_TEXT_TO_SPEECH and 
                settings.OPENAI_API_KEY and 
                settings.ENABLE_OPENAI_INTEGRATION and
                self.openai_service):
                
                try:
                    # Use simple OpenAI TTS
                    audio_data = await self.openai_service.generate_speech(text_content)
                    
                    if audio_data:
                        # Save audio data to file
                        audio_filename = f"openai_tts_{uuid.uuid4().hex}.mp3"
                        audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'output', audio_filename)
                        
                        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                        
                        with open(audio_path, 'wb') as f:
                            f.write(audio_data)
                        
                        logger.info(f"✅ Generated OpenAI TTS audio: {audio_filename}")
                        return f"/media/audio/output/{audio_filename}"
                    
                except Exception as openai_error:
                    logger.warning(f"❌ OpenAI TTS failed: {openai_error}")
            
            logger.info("🔊 Using browser TTS (no server-side audio generation)")
            return None  # Let browser handle TTS
            
        except Exception as e:
            logger.error(f"❌ TTS Error: {e}")
            return None

