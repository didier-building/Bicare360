"""
ASGI config for bicare360 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/

This configuration supports both HTTP and WebSocket connections:
- HTTP requests are handled by Django's standard request/response cycle
- WebSocket connections are handled by Django Channels for real-time chat

Author: Didier IMANIRAHARI
Date: February 2026
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bicare360.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import WebSocket routing after Django initialization
# This must happen after get_asgi_application() to avoid AppRegistryNotReady error
from apps.chat import routing as chat_routing

# ASGI application configuration
# Routes connections based on protocol type (http vs websocket)
application = ProtocolTypeRouter(
    {
        # Django's ASGI application handles traditional HTTP requests
        "http": django_asgi_app,
        
        # WebSocket chat application with authentication and security
        "websocket": AllowedHostsOriginValidator(  # Validate origin header
            AuthMiddlewareStack(  # Add user authentication to WebSocket scope
                URLRouter(
                    chat_routing.websocket_urlpatterns  # Chat WebSocket routes
                )
            )
        ),
    }
)
