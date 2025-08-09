from django.db import models
import uuid


class GestureLibrary(models.Model):
    GESTURE_CATEGORIES = [
        ('immediate', 'Immediate'),
        ('contextual', 'Contextual'),
        ('emotional', 'Emotional'),
        ('professional', 'Professional'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=GESTURE_CATEGORIES)
    animation_data = models.JSONField()
    duration = models.FloatField(help_text="Duration in seconds")
    trigger_keywords = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class AnimationSequence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField()
    gestures = models.ManyToManyField(GestureLibrary, through='AnimationFrame')
    total_duration = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Animation Sequence {self.id}"


class AnimationFrame(models.Model):
    sequence = models.ForeignKey(AnimationSequence, on_delete=models.CASCADE)
    gesture = models.ForeignKey(GestureLibrary, on_delete=models.CASCADE)
    start_time = models.FloatField()
    end_time = models.FloatField()
    intensity = models.FloatField(default=1.0)
    
    class Meta:
        ordering = ['start_time']