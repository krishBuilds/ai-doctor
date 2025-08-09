import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Session, Conversation
from .services import ChatService


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.session = None
        self.chat_service = ChatService()
        print("[INIT] ChatConsumer initialized - NO STREAMING")

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
        print(f"🔴 CONSUMER: Raw message received: {text_data}")
        data = json.loads(text_data)
        message_type = data.get('type')
        print(f"🔴 CONSUMER: Message type: {message_type}")
        
        if message_type == 'chat_message':
            print(f"🔴 CONSUMER: Handling chat message")
            await self.handle_chat_message(data)
        elif message_type == 'voice_input':
            await self.handle_voice_input(data)
        elif message_type == 'gesture_trigger':
            await self.handle_gesture_trigger(data)
        else:
            print(f"🔴 CONSUMER: Unknown message type: {message_type}")

    async def handle_chat_message(self, data):
        user_message = data['message']
        print(f"[CONSUMER] Received: {user_message}")
        
        try:
            # Get AI response
            ai_response_data = await self.chat_service.get_medical_response(
                user_message, 
                self.session_id
            )
            
            ai_message = ai_response_data.get('message', 'Sorry, I could not generate a response.')
            print(f"[CONSUMER] Sending: {ai_message[:50]}...")
            
            # Send ONLY simple message - NO OTHER MESSAGE TYPES
            await self.send(text_data=json.dumps({
                'type': 'message',
                'message': ai_message,
                'sender': 'ai',
                'gesture': 'professional',
                'mood': 'professional',
                'audio_url': None,
                'gestures': []
            }))
            print(f"[SUCCESS] Direct message sent")
            
        except Exception as e:
            print(f"[ERROR] {e}")
            await self.send(text_data=json.dumps({
                'type': 'message',
                'message': 'Sorry, I encountered an error. Please try again.',
                'sender': 'ai',
                'gesture': 'professional',
                'mood': 'professional',
                'audio_url': None,
                'gestures': []
            }))
    
    async def handle_voice_input(self, data):
        transcription = data.get('transcription', '')
        if transcription:
            await self.handle_chat_message({'message': transcription})

    async def handle_gesture_trigger(self, data):
        # Simple gesture handling - no group sends
        print(f"[GESTURE] {data.get('gesture', 'none')}")

    @database_sync_to_async
    def get_or_create_session(self):
        session, created = Session.objects.get_or_create(
            id=self.session_id,
            defaults={'is_active': True}
        )
        return session


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