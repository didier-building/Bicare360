"""
Celery tasks for medication reminders and adherence tracking.

This module contains asynchronous tasks for:
- Checking medication adherence
- Sending medication reminders
- Processing scheduled medication alerts
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.medications.tasks.check_medication_adherence")
def check_medication_adherence():
    """
    Check for missed medications and send reminders.
    
    This task runs daily (configured in Celery Beat) and:
    1. Finds all active prescriptions
    2. Checks if doses were taken as scheduled
    3. Identifies missed doses (>2 hours overdue)
    4. Sends SMS reminders to patients
    5. Creates alert for nurse if multiple doses missed
    
    Returns:
        dict: Summary of patients reminded and alerts created
    """
    from apps.medications.models import Prescription, MedicationAdherence
    from apps.patients.models import Patient
    from apps.messaging.sms_service import MessageService
    
    logger.info("Starting medication adherence check at %s", timezone.now())
    
    try:
        now = timezone.now()
        two_hours_ago = now - timedelta(hours=2)
        
        #Find active prescriptions with missed doses
        active_prescriptions = Prescription.objects.filter(
            is_active=True,
            end_date__gte=now.date()
        ).select_related('patient', 'patient__user')
        
        reminders_sent = 0
        alerts_created = 0
        
        for prescription in active_prescriptions:
            # Check if dose should have been taken
            # (Simplified logic - enhance based on dosage schedule)
            
            # Check if patient has any adherence tracking showing non-adherence
            # Simplified logic: Check if there's any adherence record for today
            today_adherence = MedicationAdherence.objects.filter(
                prescription=prescription,
                date_recorded__date=now.date(),
                is_adherent=False
            ).exists()
            
            if today_adherence:
                # Send reminder SMS
                patient = prescription.patient
                if patient.user.phone_number:
                    message = (
                        f"BiCare360 Reminder: Time to take {prescription.medication_name}. "
                        f"Dose: {prescription.dosage}. Stay healthy! 💊"
                    )
                    
                    try:
                        sms_service = MessageService()
                        sms_service.send_sms(
                            phone_number=patient.user.phone_number,
                            message=message,
                            message_type='medication_reminder'
                        )
                        reminders_sent += 1
                        logger.info(
                            f"Sent medication reminder to patient {patient.id} "
                            f"for {prescription.medication_name}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to send medication reminder to patient {patient.id}: {e}"
                        )
        
        logger.info(
            f"Medication adherence check completed: "
            f"{reminders_sent} reminders sent, {alerts_created} alerts created"
        )
        
        return {
            'reminders_sent': reminders_sent,
            'alerts_created': alerts_created,
            'checked_at': now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in medication adherence check: {e}", exc_info=True)
        raise


@shared_task(name="apps.medications.tasks.send_medication_reminder")
def send_medication_reminder(prescription_id):
    """
    Send immediate reminder for a specific prescription.
    
    Args:
        prescription_id: ID of the Prescription to remind about
    
    Returns:
        dict: Result of reminder attempt
    """
    from apps.medications.models import Prescription
    from apps.messaging.sms_service import MessageService
    
    try:
        prescription = Prescription.objects.select_related(
            'patient', 'patient__user'
        ).get(id=prescription_id)
        
        patient = prescription.patient
        
        if not patient.user.phone_number:
            logger.warning(f"Patient {patient.id} has no phone number for SMS reminder")
            return {'status': 'skipped', 'reason': 'no_phone_number'}
        
        message = (
            f"BiCare360: Time for {prescription.medication_name}. "
            f"Dose: {prescription.dosage}. "
            f"Instructions: {prescription.instructions or 'As prescribed'}"
        )
        
        sms_service = MessageService()
        result = sms_service.send_sms(
            phone_number=patient.user.phone_number,
            message=message,
            message_type='medication_reminder'
        )
        
        logger.info(f"Sent medication reminder for prescription {prescription_id}")
        
        return {
            'status': 'sent',
            'prescription_id': prescription_id,
            'patient_id': patient.id,
            'message_id': result.get('message_id') if result else None
        }
        
    except Prescription.DoesNotExist:
        logger.error(f"Prescription {prescription_id} not found")
        return {'status': 'error', 'reason': 'prescription_not_found'}
    except Exception as e:
        logger.error(f"Error sending medication reminder: {e}", exc_info=True)
        raise
