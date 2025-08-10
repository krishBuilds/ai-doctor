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
        """Get chat response using simple OpenAI service - NON-STREAMING"""
        try:
            print(f"[INFO] ChatService: Processing message: {user_message}")
            
            # Get conversation history 
            conversation_history = await self.get_conversation_history(session_id)
            
            # Debug: Check settings
            print(f"[INFO] ENABLE_OPENAI_INTEGRATION: {settings.ENABLE_OPENAI_INTEGRATION}")
            print(f"[INFO] openai_service exists: {self.openai_service is not None}")
            
            # Use simple OpenAI service
            if settings.ENABLE_OPENAI_INTEGRATION and self.openai_service:
                print(f"[INFO] ChatService: Using OpenAI integration")
                try:
                    response_data = await self.openai_service.get_chat_response(
                        user_message=user_message,
                        conversation_history=conversation_history
                    )
                    
                    print(f"[SUCCESS] ChatService: Got OpenAI response: {response_data.get('response', '')[:50]}...")
                    
                    # Return response for frontend
                    return {
                        'message': response_data['response'],
                        'gesture': response_data.get('gesture', 'professional'),
                        'mood': response_data.get('mood', 'professional'),
                        'urgency': response_data.get('urgency', 'low'),
                        'type': response_data.get('type', 'ai_response')
                    }
                except Exception as openai_error:
                    print(f"[ERROR] OpenAI Error: {openai_error}")
                    return await self.get_fallback_response(user_message)
            else:
                print(f"[WARN] ChatService: Using fallback response - OpenAI not available")
                print(f"   - ENABLE_OPENAI_INTEGRATION: {settings.ENABLE_OPENAI_INTEGRATION}")
                print(f"   - openai_service: {self.openai_service}")
                # Fallback response
                return await self.get_fallback_response(user_message)
                
        except Exception as e:
            print(f"[ERROR] ChatService Exception: {e}")
            logger.error(f"❌ Error getting chat response: {e}")
            return {
                'message': "I apologize, I'm experiencing technical difficulties. Please try again in a moment.",
                'gesture': 'professional',
                'mood': 'professional',
                'urgency': 'low',
                'type': 'error'
            }

    async def get_streaming_medical_response(self, user_message, session_id, stream_callback=None):
        """Get STREAMING chat response using OpenAI with real-time callbacks"""
        try:
            print(f"[STREAM] ChatService: Starting streaming response for: {user_message}")
            
            # Get conversation history 
            conversation_history = await self.get_conversation_history(session_id)
            
            # Use OpenAI streaming service
            if settings.ENABLE_OPENAI_INTEGRATION and self.openai_service:
                print(f"[STREAM] ChatService: Using OpenAI streaming integration")
                try:
                    response_data = await self.openai_service.get_streaming_chat_response(
                        user_message=user_message,
                        conversation_history=conversation_history,
                        callback=stream_callback
                    )
                    
                    print(f"[STREAM] ChatService: Streaming complete: {response_data.get('response', '')[:50]}...")
                    
                    # Return final response data
                    return {
                        'message': response_data['response'],
                        'gesture': response_data.get('gesture', 'professional'),
                        'mood': response_data.get('mood', 'professional'),
                        'urgency': response_data.get('urgency', 'low'),
                        'type': response_data.get('type', 'ai_stream_response')
                    }
                except Exception as openai_error:
                    print(f"[ERROR] OpenAI Streaming Error: {openai_error}")
                    # Fall back to regular response
                    return await self.get_medical_response(user_message, session_id)
            else:
                print(f"[WARN] ChatService: OpenAI not available, using regular response")
                # Fall back to regular response
                return await self.get_medical_response(user_message, session_id)
                
        except Exception as e:
            print(f"[ERROR] ChatService Streaming Exception: {e}")
            logger.error(f"❌ Error getting streaming chat response: {e}")
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
        print(f"🟡 Using fallback response for: {user_message}")
        
        responses = {
            "hello": "Hello! I'm Dr. AI, your virtual medical assistant. How can I help you today?",
            "pain": "I understand you're experiencing pain. Can you describe where the pain is located and how severe it is on a scale of 1-10?",
            "fever": "A fever can indicate various conditions. Have you taken your temperature? Any other symptoms like headache or body aches?",
            "feverish": "I understand you're feeling feverish. This could be a sign of infection or illness. Have you taken your temperature? Any other symptoms like chills, headache, or body aches? If your fever is high (over 103°F/39.4°C) or you're experiencing severe symptoms, please seek immediate medical attention.",
            "appointment": "I can help provide general health information, but for specific medical concerns, I recommend scheduling an appointment with your healthcare provider.",
        }
        
        user_lower = user_message.lower()
        for keyword, response in responses.items():
            if keyword in user_lower:
                print(f"🟡 Fallback matched '{keyword}': {response[:30]}...")
                return {
                    'message': response,
                    'gesture': 'professional',
                    'mood': 'professional',
                    'urgency': 'low',
                    'type': 'fallback_response'
                }
        
        fallback_msg = "I'm here to help with your health questions. Could you please provide more details about your symptoms or concerns?"
        print(f"🟡 Using generic fallback: {fallback_msg[:30]}...")
        return {
            'message': fallback_msg,
            'gesture': 'professional',
            'mood': 'professional', 
            'urgency': 'low',
            'type': 'fallback_response'
        }

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
        """Generate speech - optimized for speed, fallback to browser TTS"""
        # Return None immediately to use browser TTS for zero latency
        # Server TTS can be added later if needed
        return None

