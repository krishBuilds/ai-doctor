"""
Simple OpenAI Integration Service
Reads API key from .env file and provides chat responses
"""

import os
import openai
from openai import AsyncOpenAI
import logging
import json
import asyncio
from django.conf import settings

logger = logging.getLogger(__name__)

class SimpleOpenAIService:
    """Simple OpenAI service for chat and TTS"""
    
    def __init__(self):
        self.client = None
        self.async_client = None
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
            
            # Initialize both sync and async clients
            self.client = openai.OpenAI(
                api_key=api_key,
                timeout=60.0,
                max_retries=2
            )
            
            # Initialize async client for streaming
            self.async_client = AsyncOpenAI(
                api_key=api_key,
                timeout=60.0,
                max_retries=2
            )
            
            print("[SUCCESS] OpenAI clients initialized successfully (sync + async)")
            logger.info("✅ OpenAI clients initialized successfully (sync + async)")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize OpenAI client: {e}")
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.client = None
            self.async_client = None
    
    async def get_chat_response(self, user_message, conversation_history=None):
        """Get simple chat response from OpenAI - NON-STREAMING VERSION"""
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

    async def get_streaming_chat_response(self, user_message, conversation_history=None, callback=None):
        """Get STREAMING chat response from OpenAI with real-time callbacks"""
        try:
            print(f"[STREAM] OpenAI Service: Starting stream for: {user_message}")
            if not self.async_client:
                print("[ERROR] OpenAI Service: Async client not available for streaming")
                # Fall back to regular response
                regular_response = await self.get_chat_response(user_message, conversation_history)
                if callback:
                    await callback(regular_response.get('response', ''), is_final=True)
                return regular_response
            
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
            
            # Make ASYNC STREAMING API call
            print(f"[STREAM] OpenAI Service: Making ASYNC STREAMING API call to {settings.OPENAI_MODEL}")
            
            # Create the async streaming response
            response_stream = await self.async_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                stream=True  # Enable streaming
            )
            
            full_response = ""
            chunk_count = 0
            
            # Process streaming chunks asynchronously
            print(f"[STREAM] Starting to process async streaming chunks...")
            
            async for chunk in response_stream:
                chunk_count += 1
                
                # Check if this chunk has content
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    chunk_text = chunk.choices[0].delta.content
                    full_response += chunk_text
                    
                    print(f"[STREAM] Chunk {chunk_count}: {repr(chunk_text)}")
                    
                    # Send chunk to callback for real-time processing
                    if callback:
                        await callback(chunk_text, is_final=False)
                
                # Check if stream is finished
                if hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason is not None:
                    print(f"[STREAM] Stream finished. Reason: {chunk.choices[0].finish_reason}")
                    break
            
            print(f"[STREAM] Processed {chunk_count} chunks total")
            
            # Send final completion signal
            if callback:
                await callback("", is_final=True)
            
            print(f"[STREAM] Complete response (length: {len(full_response)}): {full_response[:100]}...")
            
            return {
                'response': full_response,
                'gesture': 'professional',
                'mood': 'professional',
                'urgency': 'low',
                'type': 'ai_stream_response'
            }
            
        except Exception as e:
            print(f"[ERROR] OpenAI Streaming error: {e}")
            logger.error(f"❌ OpenAI Streaming error: {e}")
            # Fall back to regular response
            return await self.get_chat_response(user_message, conversation_history)
    
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