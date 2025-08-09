from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def voice_status(request):
    """Get voice service status"""
    return Response({'status': 'Voice service running'})