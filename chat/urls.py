from django.urls import path
from . import views, api_views

app_name = 'chat'

urlpatterns = [
    # HTTP API endpoints (fallback when WebSocket fails)
    path('', api_views.ChatAPIView.as_view(), name='chat_api'),
    path('tts/', api_views.tts_api, name='tts_api'),
    path('health/', api_views.health_check, name='health_check'),
]