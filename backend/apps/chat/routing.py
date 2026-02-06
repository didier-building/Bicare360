"""
WebSocket URL Routing for BiCare360 Chat Application

This module defines WebSocket URL patterns for real-time chat functionality.
It maps WebSocket connection URLs to their respective consumer classes.

The routing structure follows Django Channels' URLRouter pattern and supports
authenticated, secure WebSocket connections for real-time messaging between
patients, caregivers, and nurses.

WebSocket Endpoints:
- ws/chat/<conversation_id>/: Real-time chat messages for a specific conversation

Security:
- Authentication handled by AuthMiddlewareStack in asgi.py
- Origin validation via AllowedHostsOriginValidator
- Object-level permissions enforced in consumer classes

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.urls import path

from apps.chat import consumers

# WebSocket URL patterns for chat functionality
# These routes handle persistent WebSocket connections for real-time messaging
websocket_urlpatterns = [
    # Real-time chat consumer for individual conversations
    # URL: ws://domain/ws/chat/<uuid:conversation_id>/
    # Handles: message sending, delivery receipts, typing indicators
    path("ws/chat/<uuid:conversation_id>/", consumers.ChatConsumer.as_asgi()),
]
