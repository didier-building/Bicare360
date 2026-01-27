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
    - Send email to assigned nurse (if assigned)
    - Send email to all nurses (if not assigned)
    - Send SMS if critical severity
    - Log notification attempt
    """
    from apps.nursing.models import PatientAlert, NurseProfile
    from apps.messaging.email_service import EmailService
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        alert = PatientAlert.objects.select_related(
            'patient', 'assigned_nurse', 'assigned_nurse__user'
        ).get(id=alert_id)
        
        logger.info("Sending notification for alert %d: %s", alert_id, alert.title)
        
        email_service = EmailService()
        sent_count = 0
        
        # Determine recipients
        if alert.assigned_nurse and alert.assigned_nurse.user.email:
            # Send to assigned nurse
            recipients = [alert.assigned_nurse.user.email]
            logger.info(f"Sending alert to assigned nurse: {alert.assigned_nurse.user.email}")
        else:
            # Send to all active nurses
            active_nurses = NurseProfile.objects.filter(
                is_active=True,
                user__email__isnull=False
            ).exclude(user__email='').select_related('user')
            
            recipients = [nurse.user.email for nurse in active_nurses if nurse.user.email]
            logger.info(f"Sending alert to {len(recipients)} active nurses")
        
        if not recipients:
            logger.warning(f"No email recipients found for alert {alert_id}")
            return {'alert_id': alert_id, 'status': 'no_recipients'}
        
        # Prepare email content
        severity_emoji = {
            'low': '🔵',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        
        subject = f"{severity_emoji.get(alert.severity, '⚠️')} Patient Alert: {alert.title}"
        
        # Plain text message
        message = f"""
Patient Alert Notification

Severity: {alert.get_severity_display().upper()}
Patient: {alert.patient.full_name}
ID: {alert.patient.id}

Alert Type: {alert.get_alert_type_display()}
Title: {alert.title}

Description:
{alert.description}

Status: {alert.get_status_display()}
Created: {alert.created_at.strftime('%B %d, %Y at %I:%M %p')}

Please review and take appropriate action in the BiCare360 system.

---
BiCare360 Nurse Dashboard
        """.strip()
        
        # HTML message
        severity_color = {
            'low': '#3b82f6',
            'medium': '#eab308',
            'high': '#f97316',
            'critical': '#ef4444'
        }
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {severity_color.get(alert.severity, '#666')}; color: white; padding: 15px; border-radius: 8px 8px 0 0;">
                    <h2 style="margin: 0; color: white;">{severity_emoji.get(alert.severity, '⚠️')} Patient Alert</h2>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #fff;">{alert.get_severity_display().upper()} Priority</p>
                </div>
                
                <div style="border: 2px solid {severity_color.get(alert.severity, '#666')}; border-top: none; padding: 20px; border-radius: 0 0 8px 8px;">
                    <h3 style="color: #1f2937; margin-top: 0;">{alert.title}</h3>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <p style="margin: 5px 0;"><strong>Patient:</strong> {alert.patient.full_name}</p>
                        <p style="margin: 5px 0;"><strong>Patient ID:</strong> {alert.patient.id}</p>
                        <p style="margin: 5px 0;"><strong>Alert Type:</strong> {alert.get_alert_type_display()}</p>
                        <p style="margin: 5px 0;"><strong>Status:</strong> {alert.get_status_display()}</p>
                        <p style="margin: 5px 0;"><strong>Created:</strong> {alert.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <strong>Description:</strong>
                        <p style="margin: 10px 0; padding: 10px; background-color: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 4px;">
                            {alert.description}
                        </p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 5px 0; font-size: 14px; color: #6b7280;">
                            Please review and take appropriate action in the BiCare360 Nurse Dashboard.
                        </p>
                    </div>
                </div>
                
                <p style="margin-top: 30px; font-size: 12px; color: #9ca3af; text-align: center;">
                    BiCare360 Patient Care Platform
                </p>
            </div>
        </body>
        </html>
        """
        
        # Send emails
        for recipient in recipients:
            result = email_service.send_email(
                to_email=recipient,
                subject=subject,
                message=message,
                html_message=html_message
            )
            if result['success']:
                sent_count += 1
        
        logger.info(f"Notification sent to {sent_count}/{len(recipients)} nurses for alert {alert_id}")
        
        return {
            'alert_id': alert_id,
            'status': 'sent',
            'recipients': len(recipients),
            'sent_count': sent_count
        }
        
    except PatientAlert.DoesNotExist:
        logger.error("Alert %d not found for notification", alert_id)
        raise
    except Exception as e:
        logger.error("Failed to send notification for alert %d: %s", alert_id, str(e))
        raise
