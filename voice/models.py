from django.db import models
import uuid


class AudioProcessing(models.Model):
    PROCESSING_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField()
    audio_file = models.FileField(upload_to='audio/input/')
    transcription = models.TextField(blank=True)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    processing_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Audio Processing {self.id} - {self.processing_status}"


class TTSOutput(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField()
    text = models.TextField()
    audio_file = models.FileField(upload_to='audio/output/')
    voice_settings = models.JSONField(default=dict, blank=True)
    lip_sync_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"TTS Output {self.id}"