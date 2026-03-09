#!/usr/bin/env python
"""
Quick test script to verify Celery can connect to Redis broker.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from bicare360.celery import app
from celery import Celery

def test_celery_connection():
    """Test Celery Redis broker connection"""
    print("Testing Celery Configuration...")
    print(f"Broker URL: {app.conf.broker_url}")
    print(f"Result Backend: {app.conf.result_backend}")
    
    # Inspect Celery
    try:
        # Test broker connection
        conn = app.connection()
        conn.ensure_connection(max_retries=3)
        print("✓ Broker connection successful")
        conn.release()
        
        # Get registered tasks
        registered_tasks = list(app.tasks.keys())
        print(f"\n✓ Found {len(registered_tasks)} registered tasks:")
        for task in sorted(registered_tasks)[:10]:  # Show first 10
            if not task.startswith('celery.'):
                print(f"  - {task}")
        
        print("\n✅ Celery is configured and ready!")
        return True
        
    except Exception as e:
        print(f"\n❌ Celery broker connection failed: {e}")
        return False

if __name__ == "__main__":
    result = test_celery_connection()
    exit(0 if result else 1)
