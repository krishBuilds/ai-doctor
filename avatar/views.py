from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def avatar_status(request):
    """Get avatar status"""
    return Response({'status': 'Avatar service running'})