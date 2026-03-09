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
    # Run alert engine every 10 minutes
    "run-alert-engine": {
        "task": "apps.nursing.tasks.run_alert_engine",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
    },
    # Send appointment email reminders daily at 8 AM
    "send-appointment-email-reminders": {
        "task": "apps.messaging.tasks.send_appointment_reminder_emails",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8:00 AM
    },
    # Send medication email reminders daily at 9 AM and 8 PM
    "send-medication-email-reminders-morning": {
        "task": "apps.messaging.tasks.send_medication_reminder_emails",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9:00 AM
    },
    "send-medication-email-reminders-evening": {
        "task": "apps.messaging.tasks.send_medication_reminder_emails",
        "schedule": crontab(hour=20, minute=0),  # Daily at 8:00 PM
    },
    # NEW: Check medication adherence daily at 8 AM
    "check-medication-adherence": {
        "task": "apps.medications.tasks.check_medication_adherence",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8:00 AM
    },
    # NEW: Send appointment SMS reminders daily at 9 AM
    "send-appointment-sms-reminders": {
        "task": "apps.appointments.tasks.send_appointment_reminders",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9:00 AM
    },
    # NEW: Check for missed appointments every hour
    "notify-missed-appointments": {
        "task": "apps.appointments.tasks.notify_missed_appointments",
        "schedule": crontab(minute=0),  # Every hour at :00
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
