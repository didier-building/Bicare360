#!/usr/bin/env python
"""
Test Celery tasks are working.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from apps.medications.tasks import check_medication_adherence, send_medication_reminder
from apps.appointments.tasks import send_appointment_reminders, send_appointment_confirmation
from apps.messaging.tasks import process_message_queue
from apps.nursing.tasks import run_alert_engine

print("✅ All tasks imported successfully!\n")

print("Available tasks:")
print("  📋 Medications:")
print("     - check_medication_adherence")
print("     - send_medication_reminder")
print("\n  📅 Appointments:")
print("     - send_appointment_reminders")
print("     - send_appointment_confirmation")
print("\n  💬 Messaging:")
print("     - process_message_queue")
print("\n  🏥 Nursing:")
print("     - run_alert_engine")

print("\n" + "="*60)
print("Testing task execution...")
print("="*60 + "\n")

# Test running tasks synchronously (not async)
try:
    print("1. Testing medication adherence check...")
    result = check_medication_adherence()
    print(f"   ✓ Result: {result}\n")
except Exception as e:
    print(f"   ✗ Error: {e}\n")

try:
    print("2. Testing appointment reminders...")
    result = send_appointment_reminders()
    print(f"   ✓ Result: {result}\n")
except Exception as e:
    print(f"   ✗ Error: {e}\n")

print("="*60)
print("✅ Task testing complete!")
print("="*60)
print("\nTo run tasks asynchronously with Celery:")
print("  1. Start worker: celery -A bicare360 worker -l info")
print("  2. Start beat: celery -A bicare360 beat -l info")
print("  3. Or both: celery -A bicare360 worker -B -l info")
