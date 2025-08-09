import json
import re
from channels.db import database_sync_to_async
from .models import GestureLibrary


class AnimationService:
    def __init__(self):
        self.gesture_keywords = {
            'wave': ['hello', 'hi', 'greeting', 'welcome'],
            'nod': ['yes', 'agree', 'understand', 'correct'],
            'think': ['let me think', 'considering', 'hmm', 'analyzing'],
            'explain': ['because', 'reason', 'explain', 'due to'],
            'empathy': ['sorry', 'understand your concern', 'sympathize'],
            'concern': ['worried', 'concerned', 'serious', 'urgent'],
            'point': ['here', 'this', 'that', 'look at'],
            'check_chart': ['medical history', 'records', 'chart', 'previous']
        }

    async def analyze_text_for_gestures(self, text):
        gestures = []
        
        # Handle both string and dict inputs
        if isinstance(text, dict):
            # Extract text from dict (likely from OpenAI response)
            text_content = text.get('response', '') or text.get('message', '') or str(text)
        elif isinstance(text, str):
            text_content = text
        else:
            text_content = str(text)
            
        text_lower = text_content.lower()
        
        # Immediate gestures (quick responses)
        if any(word in text_lower for word in ['hello', 'hi', 'welcome']):
            gestures.append({'name': 'wave', 'timing': 0, 'duration': 2.0})
        
        if any(word in text_lower for word in ['yes', 'correct', 'exactly']):
            gestures.append({'name': 'nod', 'timing': 0.5, 'duration': 1.5})
        
        # Contextual gestures based on content
        sentences = text_content.split('.')
        for i, sentence in enumerate(sentences):
            timing = i * 3.0  # Approximate timing based on sentence position
            
            if 'explain' in sentence.lower() or 'because' in sentence.lower():
                gestures.append({'name': 'explain', 'timing': timing, 'duration': 2.5})
            
            if any(word in sentence.lower() for word in ['sorry', 'understand your concern']):
                gestures.append({'name': 'empathy', 'timing': timing, 'duration': 2.0})
            
            if any(word in sentence.lower() for word in ['worried', 'serious', 'urgent']):
                gestures.append({'name': 'concern', 'timing': timing, 'duration': 2.0})
        
        return gestures

    async def get_gesture_animation_data(self, gesture_name):
        try:
            @database_sync_to_async
            def get_gesture():
                return GestureLibrary.objects.get(name=gesture_name, is_active=True)
            
            gesture = await get_gesture()
            return gesture.animation_data
        except:
            return self.get_default_gesture_data(gesture_name)

    def get_default_gesture_data(self, gesture_name):
        default_gestures = {
            'wave': {
                'bone_rotations': [
                    {'bone': 'rightUpperArm', 'rotation': [0, 0, -45], 'duration': 0.5},
                    {'bone': 'rightLowerArm', 'rotation': [0, 0, -90], 'duration': 0.5},
                    {'bone': 'rightHand', 'rotation': [0, 45, 0], 'duration': 1.0}
                ]
            },
            'nod': {
                'bone_rotations': [
                    {'bone': 'head', 'rotation': [15, 0, 0], 'duration': 0.3},
                    {'bone': 'head', 'rotation': [-15, 0, 0], 'duration': 0.3},
                    {'bone': 'head', 'rotation': [0, 0, 0], 'duration': 0.3}
                ]
            },
            'think': {
                'bone_rotations': [
                    {'bone': 'rightUpperArm', 'rotation': [0, 0, -30], 'duration': 1.0},
                    {'bone': 'rightLowerArm', 'rotation': [0, 0, -120], 'duration': 1.0},
                    {'bone': 'rightHand', 'rotation': [0, 0, 0], 'duration': 1.0}
                ]
            },
            'explain': {
                'bone_rotations': [
                    {'bone': 'rightUpperArm', 'rotation': [0, 0, -60], 'duration': 1.0},
                    {'bone': 'leftUpperArm', 'rotation': [0, 0, 60], 'duration': 1.0}
                ]
            }
        }
        
        return default_gestures.get(gesture_name, {'bone_rotations': []})

    async def generate_lip_sync_data(self, text, audio_duration):
        # Simple phoneme mapping for lip sync
        phoneme_map = {
            'A': ['a', 'ah', 'ay'],
            'E': ['e', 'eh', 'ee'],
            'I': ['i', 'ih', 'eye'],
            'O': ['o', 'oh', 'oo'],
            'U': ['u', 'uh', 'you'],
            'M': ['m', 'p', 'b'],
            'L': ['l', 'th'],
            'S': ['s', 'sh', 'ch'],
            'T': ['t', 'd', 'k', 'g']
        }
        
        words = text.lower().split()
        lip_sync_frames = []
        time_per_word = audio_duration / len(words) if words else 0
        
        for i, word in enumerate(words):
            start_time = i * time_per_word
            
            # Simple phoneme detection
            for phoneme, sounds in phoneme_map.items():
                if any(sound in word for sound in sounds):
                    lip_sync_frames.append({
                        'time': start_time,
                        'phoneme': phoneme,
                        'intensity': 0.8
                    })
                    break
        
        return lip_sync_frames