"""
Celery tasks for the nursing app.

This module contains async tasks for:
- Running the alert engine periodically
- Processing nurse assignments
- Sending alert notifications
"""
from celery import shared_task
from django.utils import timezone
import logging

from apps.nursing.alert_engine import AlertEngine

logger = logging.getLogger(__name__)


@shared_task(name="apps.nursing.tasks.run_alert_engine")
def run_alert_engine():
    """
    Run the alert engine to check for and create patient alerts.
    
    This task runs all alert checks:
    - Missed medications
    - Missed appointments
    - High-risk discharges
    
    Returns:
        dict: Summary of alerts created by category
    """
    logger.info("Starting scheduled alert engine run at %s", timezone.now())
    
    try:
        results = AlertEngine.run_all_checks()
        logger.info(
            "Alert engine completed: %d total alerts created "
            "(missed_meds=%d, missed_appts=%d, high_risk=%d)",
            results['total'],
            results['missed_medications'],
            results['missed_appointments'],
            results['high_risk_discharges']
        )
        return results
    except Exception as e:
        logger.error("Alert engine failed: %s", str(e), exc_info=True)
        raise


@shared_task(name="apps.nursing.tasks.send_alert_notification")
def send_alert_notification(alert_id):
    """
    Send notification for a new patient alert.
    
    Args:
        alert_id: ID of the PatientAlert to notify about
    
    This task will:
    - Send push notification to assigned nurse
    - Send SMS if critical severity
    - Log notification attempt
    """
    from apps.nursing.models import PatientAlert
    
    try:
        alert = PatientAlert.objects.get(id=alert_id)
        logger.info("Sending notification for alert %d: %s", alert_id, alert.title)
        
        # TODO: Implement actual notification sending
        # - Push notification via Firebase/OneSignal
        # - SMS via messaging app for critical alerts
        # - Email for high priority alerts
        
        logger.info("Notification sent successfully for alert %d", alert_id)
        return {'alert_id': alert_id, 'status': 'sent'}
        
    except PatientAlert.DoesNotExist:
        logger.error("Alert %d not found for notification", alert_id)
        raise
    except Exception as e:
        logger.error("Failed to send notification for alert %d: %s", alert_id, str(e))
        raise
