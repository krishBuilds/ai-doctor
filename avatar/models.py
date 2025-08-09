from django.db import models
import uuid


class AvatarModel(models.Model):
    AVATAR_TYPES = [
        ('vrm', 'VRM Model'),
        ('ready_player_me', 'Ready Player Me'),
        ('mixamo', 'Mixamo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    avatar_type = models.CharField(max_length=20, choices=AVATAR_TYPES)
    model_file = models.FileField(upload_to='avatars/models/')
    thumbnail = models.ImageField(upload_to='avatars/thumbnails/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class AvatarState(models.Model):
    EMOTIONS = [
        ('neutral', 'Neutral'),
        ('happy', 'Happy'),
        ('concerned', 'Concerned'),
        ('empathetic', 'Empathetic'),
        ('thinking', 'Thinking'),
    ]
    
    session_id = models.UUIDField()
    current_emotion = models.CharField(max_length=20, choices=EMOTIONS, default='neutral')
    is_speaking = models.BooleanField(default=False)
    current_gesture = models.CharField(max_length=50, blank=True)
    lip_sync_data = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Avatar State for session {self.session_id}"