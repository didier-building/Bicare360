"""
URL Configuration for BiCare360 Chat API

This module defines URL patterns for chat API endpoints using
Django REST Framework routers.

Endpoints:
    - /api/chat/conversations/ - Conversation management
    - /api/chat/messages/ - Message management

Router automatically generates:
    - List, Create, Retrieve, Update, Delete endpoints
    - Custom action endpoints (mark-as-read, soft-delete)

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.chat import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r"conversations", views.ConversationViewSet, basename="conversation")
router.register(r"messages", views.ChatMessageViewSet, basename="message")

# App namespace for URL reversing
app_name = "chat"

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
