"""
Celery configuration for Bicare360 project.

This module configures Celery for async task processing including:
- SMS/WhatsApp message sending
- Message queue processing
- Failed message retry logic
- Scheduled reminder processing
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bicare360.settings.dev")

# Create Celery app
app = Celery("bicare360")

# Load configuration from Django settings with 'CELERY_' prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Configure periodic tasks using Celery Beat
app.conf.beat_schedule = {
    # Process message queue every 5 minutes
    "process-message-queue": {
        "task": "apps.messaging.tasks.process_message_queue",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    # Retry failed messages every 15 minutes
    "retry-failed-messages": {
        "task": "apps.messaging.tasks.retry_failed_messages",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
