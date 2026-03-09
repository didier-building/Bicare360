"""
Celery tasks for appointment reminders and notifications.

This module contains asynchronous tasks for:
- Sending appointment reminders
- Processing upcoming appointments
- Notifying patients and nurses
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.appointments.tasks.send_appointment_reminders")
def send_appointment_reminders():
    """
    Send reminders for upcoming appointments in the next 24 hours.
    
    This task runs daily (configured in Celery Beat) and:
    1. Finds confirmed appointments in next 24 hours
    2. Checks if reminder already sent
    3. Sends SMS to patients
    4. Optionally sends email as well
    5. Marks reminder as sent
    
    Returns:
        dict: Summary of reminders sent
    """
    from apps.appointments.models import Appointment
    from apps.messaging.sms_service import MessageService
    
    logger.info("Starting appointment reminders check at %s", timezone.now())
    
    try:
        now = timezone.now()
        tomorrow = now + timedelta(hours=24)
        
        # Find confirmed appointments in nextmove 24 hours that haven't been reminded
        upcoming_appointments = Appointment.objects.filter(
            status__in=['confirmed', 'pending'],
            appointment_datetime__gte=now,
            appointment_datetime__lte=tomorrow,
            # Add a field to track if reminder was sent (future enhancement)
        ).select_related('patient', 'patient__user', 'hospital')
        
        reminders_sent = 0
        
        for appointment in upcoming_appointments:
            patient = appointment.patient
            
            if not patient.user.phone_number:
                logger.warning(
                    f"Patient {patient.id} has no phone number for appointment reminder"
                )
                continue
            
            # Format appointment details
            appt_time = appointment.appointment_datetime.strftime('%B %d at %I:%M %p')
            hospital_name = appointment.hospital.name if appointment.hospital else "the hospital"
            
            message = (
                f"BiCare360 Appointment Reminder:\n"
                f"You have an appointment on {appt_time} at {hospital_name}.\n"
                f"Reason: {appointment.reason or 'Follow-up'}\n"
                f"Please arrive 15 minutes early."
            )
            
            try:
                sms_service = MessageService()
                sms_service.send_sms(
                    phone_number=patient.user.phone_number,
                    message=message,
                    message_type='appointment_reminder'
                )
                
                reminders_sent += 1
                logger.info(
                    f"Sent appointment reminder to patient {patient.id} "
                    f"for appointment {appointment.id}"
                )
                
                # TODO: Mark appointment reminder as sent (add field to model)
                # appointment.reminder_sent = True
                # appointment.reminder_sent_at = now
                # appointment.save(update_fields=['reminder_sent', 'reminder_sent_at'])
                
            except Exception as e:
                logger.error(
                    f"Failed to send appointment reminder to patient {patient.id}: {e}"
                )
        
        logger.info(
            f"Appointment reminders completed: {reminders_sent} reminders sent"
        )
        
        return {
            'reminders_sent': reminders_sent,
            'checked_at': now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in appointment reminders task: {e}", exc_info=True)
        raise


@shared_task(name="apps.appointments.tasks.send_appointment_confirmation")
def send_appointment_confirmation(appointment_id):
    """
    Send confirmation SMS when appointment is created or confirmed.
    
    Args:
        appointment_id: ID of the Appointment to confirm
    
    Returns:
        dict: Result of confirmation attempt
    """
    from apps.appointments.models import Appointment
    from apps.messaging.sms_service import MessageService
    
    try:
        appointment = Appointment.objects.select_related(
            'patient', 'patient__user', 'hospital'
        ).get(id=appointment_id)
        
        patient = appointment.patient
        
        if not patient.user.phone_number:
            logger.warning(f"Patient {patient.id} has no phone number for confirmation")
            return {'status': 'skipped', 'reason': 'no_phone_number'}
        
        # Format appointment details
        appt_time = appointment.appointment_datetime.strftime('%B %d at %I:%M %p')
        hospital_name = appointment.hospital.name if appointment.hospital else "the hospital"
        
        if appointment.status == 'confirmed':
            message = (
                f"BiCare360: Your appointment is CONFIRMED for {appt_time} "
                f"at {hospital_name}. "
                f"Reason: {appointment.reason or 'Follow-up'}. "
                f"See you soon!"
            )
        else:
            message = (
                f"BiCare360: Appointment request received for {appt_time}. "
                f"We'll notify you once confirmed. Stay healthy!"
            )
        
        sms_service = MessageService()
        result = sms_service.send_sms(
            phone_number=patient.user.phone_number,
            message=message,
            message_type='appointment_confirmation'
        )
        
        logger.info(f"Sent appointment confirmation for appointment {appointment_id}")
        
        return {
            'status': 'sent',
            'appointment_id': appointment_id,
            'patient_id': patient.id,
            'message_id': result.get('message_id') if result else None
        }
        
    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found")
        return {'status': 'error', 'reason': 'appointment_not_found'}
    except Exception as e:
        logger.error(f"Error sending appointment confirmation: {e}", exc_info=True)
        raise


@shared_task(name="apps.appointments.tasks.notify_missed_appointments")
def notify_missed_appointments():
    """
    Check for missed appointments and notify nurses.
    
    This task runs periodically to identify no-shows and create alerts.
    
    Returns:
        dict: Summary of missed appointments processed
    """
    from apps.appointments.models import Appointment
    from apps.nursing.models import PatientAlert
    
    logger.info("Checking for missed appointments at %s", timezone.now())
    
    try:
        now = timezone.now()
        two_hours_ago = now - timedelta(hours=2)
        
        # Find confirmed appointments that are >2 hours past and still confirmed
        # (should have been marked completed or cancelled)
        missed_appointments = Appointment.objects.filter(
            status='confirmed',
            appointment_datetime__lt=two_hours_ago,
            appointment_datetime__gte=now - timedelta(days=1)  # Only check last 24 hours
        ).select_related('patient')
        
        alerts_created = 0
        
        for appointment in missed_appointments:
            # Create alert for nurse
            try:
                alert, created = PatientAlert.objects.get_or_create(
                    patient=appointment.patient,
                    title=f"Missed Appointment: {appointment.reason or 'Follow-up'}",
                    defaults={
                        'description': (
                            f"Patient missed appointment on "
                            f"{appointment.appointment_datetime.strftime('%B %d at %I:%M %p')}. "
                            f"Follow up recommended."
                        ),
                        'severity': 'medium',
                        'category': 'appointment',
                    }
                )
                
                if created:
                    alerts_created += 1
                    logger.info(
                        f"Created missed appointment alert for patient {appointment.patient.id}"
                    )
                
                # Mark appointment as missed (would need a 'missed' status)
                # appointment.status = 'missed'
                # appointment.save(update_fields=['status'])
                
            except Exception as e:
                logger.error(f"Error creating alert for missed appointment: {e}")
        
        logger.info(f"Missed appointments check completed: {alerts_created} alerts created")
        
        return {
            'alerts_created': alerts_created,
            'checked_at': now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking missed appointments: {e}", exc_info=True)
        raise
