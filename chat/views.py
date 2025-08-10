from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import asyncio
from .services import ChatService

# Create your views here.

@api_view(['GET'])
def chat_status(request):
    """Get chat service status"""
    return Response({'status': 'Chat service running'})

@csrf_exempt
@require_http_methods(["POST"])
def chat_message(request):
    """Handle chat messages via HTTP POST"""
    try:
        print("[HTTP] Chat message received")
        data = json.loads(request.body)
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        print(f"[HTTP] Message: {message}")
        print(f"[HTTP] Session: {session_id}")
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get AI response using the same service as WebSocket
        chat_service = ChatService()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            ai_response = loop.run_until_complete(
                chat_service.get_medical_response(message, session_id)
            )
            
            print(f"[HTTP] AI Response: {ai_response.get('message', '')[:50]}...")
            
            return JsonResponse({
                'message': ai_response.get('message', 'Sorry, I could not generate a response.'),
                'gesture': ai_response.get('gesture', 'professional'),
                'mood': ai_response.get('mood', 'professional'),
                'sender': 'ai'
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        print(f"[HTTP] Error: {e}")
        return JsonResponse({
            'message': 'Sorry, I encountered an error. Please try again.',
            'sender': 'ai'
        })