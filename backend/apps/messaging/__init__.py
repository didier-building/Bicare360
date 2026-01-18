"""
Messaging application for SMS and WhatsApp notifications.

This app handles:
- SMS and WhatsApp message sending via Africa's Talking API
- Message templates (English and Kinyarwanda)
- Automated appointment reminders
- Message delivery tracking and retry logic
- Message queue management
"""

default_app_config = "apps.messaging.apps.MessagingConfig"
