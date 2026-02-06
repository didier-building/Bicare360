"""
Chat Application Configuration

This module configures the BiCare360 real-time chat application that enables
secure, HIPAA-compliant messaging between patients, caregivers, and nurses.

The chat system supports:
- Patient-to-Caregiver communication for daily care coordination
- Patient-to-Nurse communication for medical support and monitoring
- Caregiver-to-Nurse communication for care team collaboration
- File attachments (images, documents) with S3 storage
- Read receipts and delivery status tracking
- Message notifications and unread counters
- Soft delete for message management

Technical Implementation:
- Django Channels for WebSocket real-time communication
- Redis as channel layer backend for message distribution
- JWT authentication for WebSocket connections
- Object-level permissions via django-guardian

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.apps import AppConfig


class ChatConfig(AppConfig):
    """
    Django application configuration for the BiCare360 chat system.
    
    This app provides real-time messaging functionality between platform users,
    with support for attachments, notifications, and read status tracking.
    
    Attributes:
        default_auto_field (str): Primary key field type for models (BigAutoField)
        name (str): Full Python path to the application package
    """
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
