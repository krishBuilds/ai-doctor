"""
Simple OpenAI Integration Service
Reads API key from .env file and provides chat responses
"""

import os
import openai
import logging
import json
import asyncio
from django.conf import settings

logger = logging.getLogger(__name__)

class SimpleOpenAIService:
    """Simple OpenAI service for chat and TTS"""
    
    def __init__(self):
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize OpenAI client with API key from .env"""
        try:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                print("[ERROR] OPENAI_API_KEY not found in .env file")
                logger.warning("OPENAI_API_KEY not found in .env file")
                return
            
            print(f"[INFO] Initializing OpenAI client with API key: {api_key[:10]}...")
            print(f"[INFO] OpenAI module version: {openai.__version__}")
            logger.info(f"Initializing OpenAI client with API key: {api_key[:10]}...")
            logger.info(f"OpenAI module version: {openai.__version__}")
            
            # Correct OpenAI client initialization for v1.10.0+
            self.client = openai.OpenAI(
                api_key=api_key,
                timeout=60.0,
                max_retries=2
            )
            print("[SUCCESS] OpenAI client initialized successfully")
            logger.info("✅ OpenAI client initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize OpenAI client: {e}")
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.client = None
    
    async def get_chat_response(self, user_message, conversation_history=None):
        """Get simple chat response from OpenAI"""
        try:
            print(f"[INFO] OpenAI Service: Processing message: {user_message}")
            if not self.client:
                print("[ERROR] OpenAI Service: Client not available, using fallback")
                return self._get_fallback_response(user_message)
            
            # Build messages with medical context
            messages = [
                {
                    "role": "system", 
                    "content": """You are Dr. AI, a compassionate virtual medical assistant. 

Guidelines:
- Provide helpful, accurate health information based on medical knowledge
- Always recommend consulting healthcare professionals for serious concerns
- Be empathetic and understanding in your responses
- Ask clarifying questions when needed to better understand symptoms
- Never provide specific diagnoses or prescriptions
- Focus on general wellness, health education, and symptom guidance
- Keep responses clear, structured, and easy to understand
- If symptoms seem serious, emphasize seeking immediate medical attention

Respond in a warm, professional manner as a caring doctor would. Structure your responses with clear points when giving health advice."""
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Make API call
            print(f"[INFO] OpenAI Service: Making API call to {settings.OPENAI_MODEL}")
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            response_text = response.choices[0].message.content
            print(f"[SUCCESS] OpenAI Service: Got response (length: {len(response_text)}): {response_text[:100]}...")
            
            logger.info(f"✅ OpenAI response generated (length: {len(response_text)})")
            
            return {
                'response': response_text,
                'gesture': 'professional',
                'mood': 'professional',
                'urgency': 'low',
                'type': 'ai_response'
            }
            
        except Exception as e:
            print(f"[ERROR] OpenAI API error: {e}")
            logger.error(f"❌ OpenAI API error: {e}")
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message):
        """Simple fallback responses when OpenAI is unavailable"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            response = "Hello! I'm your AI assistant. How can I help you today?"
        elif any(word in user_lower for word in ['help', 'assist']):
            response = "I'm here to help! Please let me know what you need assistance with."
        elif any(word in user_lower for word in ['how are you', 'how do you do']):
            response = "I'm doing well, thank you for asking! How can I assist you today?"
        elif any(word in user_lower for word in ['thank', 'thanks']):
            response = "You're welcome! Is there anything else I can help you with?"
        else:
            response = "I understand you're asking about that. Could you please provide more details so I can better assist you?"
        
        return {
            'response': response,
            'gesture': 'professional',
            'mood': 'professional',
            'urgency': 'low',
            'type': 'fallback'
        }
    
    async def generate_speech(self, text):
        """Generate speech using OpenAI TTS"""
        try:
            if not self.client:
                logger.warning("OpenAI TTS not available - client not initialized")
                return None
            
            # Handle dict input
            if isinstance(text, dict):
                text_content = text.get('response', '') or text.get('message', '') or str(text)
            else:
                text_content = str(text)
            
            if not text_content.strip():
                return None
            
            # Use asyncio.to_thread to avoid async client wrapper issues
            def create_speech():
                return self.client.audio.speech.create(
                    model=settings.OPENAI_TTS_MODEL,
                    voice=settings.OPENAI_TTS_VOICE,
                    input=text_content
                )
            
            response = await asyncio.to_thread(create_speech)
            
            logger.info(f"✅ TTS audio generated for text length: {len(text_content)}")
            return response.content
            
        except Exception as e:
            logger.error(f"❌ TTS generation error: {e}")
            return None

# Global instance
simple_openai_service = SimpleOpenAIService()