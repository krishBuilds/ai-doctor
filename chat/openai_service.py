"""
OpenAI Integration Service for AI Doctor
Handles chat completions, TTS, and Whisper for medical consultations
"""

import os
import openai
import logging
import json
import asyncio
from typing import Dict, List, Optional, AsyncGenerator
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import tiktoken

logger = logging.getLogger(__name__)

class OpenAIService:
    """OpenAI API integration service for medical AI doctor"""
    
    def __init__(self):
        self.client = None
        self.rate_limiter = RateLimiter()
        self.token_counter = TokenCounter()
        self.initialize_client()
        
    def initialize_client(self):
        """Initialize OpenAI client with API key only"""
        try:
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not configured, OpenAI features will be disabled")
                self.client = None
                return
                
            # Clean initialization without deprecated parameters
            self.client = openai.OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=60.0
            )
            
            logger.info("OpenAI client initialized successfully with GPT-4o mini")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
            # Don't raise exception, just disable OpenAI features
    
    async def get_medical_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict] = None,
        patient_context: Dict = None
    ) -> Dict:
        """
        Get AI medical response using OpenAI Chat Completions
        
        Args:
            user_message: User's medical question or concern
            conversation_history: Previous conversation messages
            patient_context: Patient information (age, symptoms, etc.)
            
        Returns:
            Dict containing response text, suggested gestures, and mood
        """
        try:
            # Check if OpenAI client is available
            if not self.client:
                return self._get_fallback_response(user_message)
            
            # Check rate limits
            if not self.rate_limiter.can_make_request():
                raise Exception("Rate limit exceeded. Please try again later.")
            
            # Prepare messages
            messages = self._prepare_medical_messages(
                user_message, conversation_history, patient_context
            )
            
            # Count tokens
            token_count = self.token_counter.count_messages_tokens(messages)
            if token_count > settings.OPENAI_MAX_TOKENS * 0.8:  # Leave room for response
                messages = self._trim_conversation(messages)
            
            # Make API call
            response = await self._make_chat_completion(messages)
            
            # Parse response
            parsed_response = self._parse_medical_response(response)
            
            # Update rate limiter
            self.rate_limiter.record_request()
            
            logger.info(f"Generated medical response for query length: {len(user_message)}")
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error getting medical response: {e}")
            return self._get_fallback_response(user_message, str(e))
    
    def _prepare_medical_messages(
        self, 
        user_message: str, 
        conversation_history: List[Dict] = None,
        patient_context: Dict = None
    ) -> List[Dict]:
        """Prepare messages for OpenAI API"""
        
        # Enhanced medical system prompt
        system_prompt = self._build_medical_system_prompt(patient_context)
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        if conversation_history:
            # Limit history to prevent token overflow
            recent_history = conversation_history[-settings.MAX_CONVERSATION_HISTORY:]
            for msg in recent_history:
                if msg.get('role') in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _build_medical_system_prompt(self, patient_context: Dict = None) -> str:
        """Build professional medical system prompt with gesture integration"""
        
        # Patient context string
        context_str = ""
        if patient_context:
            context_items = []
            if patient_context.get('age'):
                context_items.append(f"Age: {patient_context['age']}")
            if patient_context.get('symptoms'):
                context_items.append(f"Symptoms: {patient_context['symptoms']}")
            if patient_context.get('medical_history'):
                context_items.append(f"History: {patient_context['medical_history']}")
            if patient_context.get('urgency_level'):
                context_items.append(f"Urgency: {patient_context['urgency_level']}")
            context_str = f"Patient: {'; '.join(context_items)}\n" if context_items else ""
        
        # Enhanced medical prompt with gesture mapping
        enhanced_prompt = f"""You are Dr. AI, a professional virtual doctor with empathy and expertise. Provide accurate medical guidance while maintaining a caring bedside manner.

{context_str}
MEDICAL GUIDELINES:
- Ask clarifying questions when needed
- Provide actionable health advice
- Always emphasize consulting healthcare professionals for serious concerns
- Be reassuring but honest about health risks
- Use medical terminology appropriately but explain complex terms

GESTURE MAPPING (choose based on interaction):
- "welcome": Greeting new patients, introductions
- "examine": Discussing symptoms, asking about physical findings
- "reassure": Providing comfort, explaining low-risk conditions
- "think": Analyzing symptoms, considering differential diagnosis
- "listen": When patient describes concerns, active listening
- "explain": Educating about conditions, treatment options
- "checkPulse": Discussing vital signs, cardiovascular concerns
- "prescribe": Recommending medications or treatments (general advice only)
- "nod": Acknowledging patient concerns, showing understanding
- "empathy": Responding to emotional distress, serious diagnoses

MOOD MAPPING:
- "professional": Standard medical consultation
- "concerned": Potentially serious symptoms requiring immediate care
- "reassuring": Mild conditions, providing comfort
- "focused": Complex medical discussions, detailed explanations

URGENCY LEVELS:
- "low": Routine questions, general health advice
- "medium": Symptoms requiring medical attention within days
- "high": Serious symptoms requiring immediate medical care

Respond in JSON:
{{
    "response": "Professional medical response with empathy and clear guidance",
    "gesture": "appropriate gesture from list above",
    "mood": "professional/concerned/reassuring/focused", 
    "urgency": "low/medium/high"
}}

Be thorough but concise. Show genuine care for patient wellbeing."""
        
        return enhanced_prompt
    
    async def _make_chat_completion(self, messages: List[Dict]) -> Dict:
        """Make the actual OpenAI API call"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_medical_response(self, response_content: str) -> Dict:
        """Parse and validate OpenAI response"""
        try:
            # Try to parse as JSON first
            parsed = json.loads(response_content)
            
            # Validate required fields
            response_data = {
                'response': parsed.get('response', response_content),
                'gesture': self._validate_gesture(parsed.get('gesture', 'professional')),
                'mood': self._validate_mood(parsed.get('mood', 'professional')),
                'urgency': parsed.get('urgency', 'low'),
                'recommendations': parsed.get('recommendations', []),
                'disclaimer': parsed.get('disclaimer', 'This information is for educational purposes only. Always consult with a qualified healthcare professional.')
            }
            
            return response_data
            
        except json.JSONDecodeError:
            # Fallback if response is not JSON
            logger.warning("Received non-JSON response from OpenAI")
            return {
                'response': response_content,
                'gesture': 'professional',
                'mood': 'professional',
                'urgency': 'low',
                'recommendations': [],
                'disclaimer': 'This information is for educational purposes only. Always consult with a qualified healthcare professional.'
            }
    
    def _validate_gesture(self, gesture: str) -> str:
        """Validate gesture name"""
        valid_gestures = [
            'welcome', 'examine', 'prescribe', 'reassure', 'checkPulse',
            'listen', 'think', 'nod', 'wave', 'point', 'explain', 'empathy'
        ]
        
        return gesture if gesture in valid_gestures else 'professional'
    
    def _validate_mood(self, mood: str) -> str:
        """Validate mood name"""
        valid_moods = ['professional', 'concerned', 'reassuring', 'focused']
        return mood if mood in valid_moods else 'professional'
    
    def _trim_conversation(self, messages: List[Dict]) -> List[Dict]:
        """Trim conversation to fit token limits"""
        # Keep system message and recent messages
        system_msg = messages[0]
        recent_messages = messages[-5:]  # Keep last 5 messages
        
        if recent_messages[0]['role'] != 'system':
            return [system_msg] + recent_messages
        else:
            return [system_msg] + recent_messages[1:]
    
    async def generate_voice_response(self, text: str, voice: str = None) -> bytes:
        """
        Generate voice response using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Audio data as bytes
        """
        try:
            if not self.client:
                raise Exception("OpenAI client not initialized")
                
            if not settings.ENABLE_TEXT_TO_SPEECH:
                raise Exception("Text-to-speech is disabled")
            
            # Handle both string and dict inputs
            if isinstance(text, dict):
                text_content = text.get('response', '') or text.get('message', '') or str(text)
            else:
                text_content = str(text)
            
            if not text_content.strip():
                raise Exception("Empty text provided for TTS")
            
            voice = voice or settings.OPENAI_TTS_VOICE
            
            # Check cache first (use text content for hash)
            cache_key = f"tts_{hash(text_content)}_{voice}"
            cached_audio = cache.get(cache_key)
            if cached_audio:
                logger.info("Returning cached TTS audio")
                return cached_audio
            
            # Generate speech synchronously to avoid async client wrapper issues
            def create_speech():
                return self.client.audio.speech.create(
                    model=settings.OPENAI_TTS_MODEL,
                    voice=voice,
                    input=text_content,
                    response_format="mp3"
                )
            
            response = await asyncio.to_thread(create_speech)
            audio_data = response.content
            
            # Cache the result
            cache.set(cache_key, audio_data, timeout=3600)  # Cache for 1 hour
            
            logger.info(f"Generated TTS audio for text length: {len(text_content)}")
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating voice response: {e}")
            raise
    
    async def transcribe_audio(self, audio_file) -> str:
        """
        Transcribe audio using OpenAI Whisper
        
        Args:
            audio_file: Audio file to transcribe
            
        Returns:
            Transcribed text
        """
        try:
            if not self.client:
                raise Exception("OpenAI client not initialized")
                
            if not settings.ENABLE_SPEECH_TO_TEXT:
                raise Exception("Speech-to-text is disabled")
            
            def create_transcription():
                return self.client.audio.transcriptions.create(
                    model=settings.OPENAI_WHISPER_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            transcript = await asyncio.to_thread(create_transcription)
            
            logger.info(f"Transcribed audio, result length: {len(transcript)}")
            
            return transcript
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def close(self):
        """Clean up client resources"""
        try:
            if self.client and hasattr(self.client, 'close'):
                self.client.close()
        except Exception as e:
            logger.error(f"Error closing OpenAI client: {e}")
    
    def _get_fallback_response(self, user_message: str, error_msg: str = None) -> Dict:
        """Get fallback response when OpenAI is not available"""
        
        # Simple keyword-based responses
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            response = "Hello! I'm Dr. AI. How can I help you with your health concerns today?"
            gesture = 'welcome'
            mood = 'professional'
        elif any(word in user_lower for word in ['pain', 'hurt', 'ache']):
            response = "I understand you're experiencing pain. Can you describe the location and severity? For immediate severe pain, please seek medical attention."
            gesture = 'examine'
            mood = 'concerned'
        elif any(word in user_lower for word in ['fever', 'temperature', 'hot']):
            response = "Fever can indicate various conditions. Have you taken your temperature? Please monitor your symptoms and consult a healthcare provider if it persists."
            gesture = 'checkPulse'
            mood = 'professional'
        elif any(word in user_lower for word in ['headache', 'head']):
            response = "For headaches, try rest, hydration, and over-the-counter pain relief if appropriate. Seek medical care for severe or persistent headaches."
            gesture = 'reassure'
            mood = 'reassuring'
        else:
            response = "I'm here to help with your health questions. Please describe your symptoms or concerns, and I'll provide general medical information. Always consult healthcare professionals for specific medical advice."
            gesture = 'listen'
            mood = 'professional'
        
        return {
            'response': response,
            'gesture': gesture,
            'mood': mood,
            'urgency': 'low',
            'fallback': True
        }


class RateLimiter:
    """Simple rate limiter for OpenAI API"""
    
    def __init__(self):
        self.requests = []
        self.max_requests = settings.OPENAI_RATE_LIMIT_RPM
        self.time_window = 60  # seconds
    
    def can_make_request(self) -> bool:
        """Check if we can make a request within rate limits"""
        now = timezone.now()
        # Remove old requests outside time window
        self.requests = [req for req in self.requests if now - req < timedelta(seconds=self.time_window)]
        
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record that a request was made"""
        self.requests.append(timezone.now())


class TokenCounter:
    """Token counting utility for OpenAI models"""
    
    def __init__(self):
        try:
            self.encoding = tiktoken.encoding_for_model(settings.OPENAI_MODEL)
        except Exception:
            # Fallback encoding
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict]) -> int:
        """Count tokens in message list"""
        total_tokens = 0
        for message in messages:
            total_tokens += self.count_tokens(message.get('content', ''))
            total_tokens += 4  # Message formatting tokens
        total_tokens += 2  # Conversation formatting
        
        return total_tokens


# Global service instance - disabled to prevent conflicts
# Services should create their own instances using get_openai_service()
openai_service = None