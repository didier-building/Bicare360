#!/usr/bin/env python
"""
Test Celery async task execution.
"""
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from apps.medications.tasks import check_medication_adherence
from apps.appointments.tasks import send_appointment_reminders

print("="*60)
print("Testing Celery Async Task Execution")
print("="*60)

# Test 1: Call task asynchronously
print("\n1. Calling check_medication_adherence.delay()...")
try:
    result = check_medication_adherence.delay()
    print(f"   ✓ Task queued with ID: {result.id}")
    print(f"   ✓ Task state: {result.state}")
    
    # Wait a bit for task to complete
    print("   Waiting for task to complete (5 seconds)...")
    time.sleep(5)
    
    if result.ready():
        print(f"   ✓ Task completed!")
        print(f"   ✓ Result: {result.result}")
    else:
        print(f"   ⚠ Task still processing... State: {result.state}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Call another task
print("\n2. Calling send_appointment_reminders.delay()...")
try:
    result = send_appointment_reminders.delay()
    print(f"   ✓ Task queued with ID: {result.id}")
    print(f"   ✓ Task state: {result.state}")
    
    time.sleep(5)
    
    if result.ready():
        print(f"   ✓ Task completed!")
        print(f"   ✓ Result: {result.result}")
    else:
        print(f"   ⚠ Task still processing... State: {result.state}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("✅ Async task testing complete!")
print("="*60)
print("\nNote: Tasks are processed by the Celery worker.")
print("Make sure worker is running: celery -A bicare360 worker -l info")
