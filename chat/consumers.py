import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Session, Conversation
from .services import ChatService, TTSService
from animation.services import AnimationService


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.session = None
        self.chat_service = ChatService()
        self.tts_service = TTSService()
        self.animation_service = AnimationService()

    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        self.session = await self.get_or_create_session()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'voice_input':
            await self.handle_voice_input(data)
        elif message_type == 'gesture_trigger':
            await self.handle_gesture_trigger(data)

    async def handle_chat_message(self, data):
        user_message = data['message']
        
        # Save user message
        await self.save_conversation('user', user_message)
        
        # Get AI response
        ai_response_data = await self.chat_service.get_medical_response(
            user_message, 
            self.session_id
        )
        
        # Extract message text
        ai_message = ai_response_data.get('message', 'Sorry, I could not generate a response.')
        
        # Save AI response 
        await self.save_conversation('ai', ai_message)
        
        # Analyze for gestures using the message text
        gestures = await self.animation_service.analyze_text_for_gestures(ai_message)
        
        # Generate TTS using the message text
        tts_audio_url = await self.tts_service.text_to_speech(ai_message, self.session_id)
        
        # Send complete response to frontend
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_response',
                'message': ai_message,
                'gesture': ai_response_data.get('gesture', 'professional'),
                'mood': ai_response_data.get('mood', 'professional'),
                'urgency': ai_response_data.get('urgency', 'low'),
                'response_type': ai_response_data.get('type', 'ai_response'),
                'audio_url': tts_audio_url,
                'gestures': gestures,
                'sender': 'ai'
            }
        )

    async def handle_voice_input(self, data):
        transcription = data.get('transcription', '')
        if transcription:
            await self.handle_chat_message({'message': transcription})

    async def handle_gesture_trigger(self, data):
        gesture_name = data.get('gesture')
        if gesture_name:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'gesture_command',
                    'gesture': gesture_name
                }
            )

    async def chat_message_response(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'audio_url': event.get('audio_url'),
            'gestures': event.get('gestures', []),
            'sender': event['sender']
        }))

    async def gesture_command(self, event):
        await self.send(text_data=json.dumps({
            'type': 'gesture',
            'gesture': event['gesture']
        }))

    @database_sync_to_async
    def get_or_create_session(self):
        session, created = Session.objects.get_or_create(
            id=self.session_id,
            defaults={'is_active': True}
        )
        return session

    @database_sync_to_async
    def save_conversation(self, message_type, content):
        return Conversation.objects.create(
            session=self.session,
            message_type=message_type,
            content=content
        )


class AvatarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'avatar_{self.session_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'avatar_update',
                'data': data
            }
        )

    async def avatar_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'avatar_state',
            'data': event['data']
        }))