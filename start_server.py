#!/usr/bin/env python
"""
Simple startup script for AI Doctor Avatar
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_doctor.settings')
    
    print("Starting AI Doctor Avatar Server...")
    print("Checking configuration...")
    
    try:
        django.setup()
        print("Django setup complete")
        print("Server will be available at: http://localhost:8000")
        print("Features available:")
        print("   - 3D Avatar with Three.js")
        print("   - Voice Input (Web Speech API)")
        print("   - Text-to-Speech (edge-tts)")
        print("   - Medical Chat Interface")
        print("   - Gesture Animations")
        print("")
        print("Starting server...")
        
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
        
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure all dependencies are installed:")
        print("   pip install -r requirements-win.txt")
        sys.exit(1)