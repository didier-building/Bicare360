"""
Celery tasks for async message processing.

This module contains all asynchronous tasks for the messaging app including:
- Sending individual messages
- Processing the message queue
- Retrying failed messages
- Bulk message operations
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from apps.messaging import services

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_message_task(self, message_id):
    """
    Send a single message asynchronously.
    
    Args:
        message_id: ID of the Message object to send
        
    Returns:
        dict: Result with status and message details
        
    This task will:
    1. Retrieve the message from database
    2. Send via appropriate provider (SMS/WhatsApp)
    3. Create MessageLog entry with result
    4. Update message status
    5. Retry on failure (max 3 times)
    """
    from apps.messaging.models import Message, MessageLog
    
    try:
        message = Message.objects.select_related(
            'recipient_patient', 'template', 'appointment'
        ).get(id=message_id)
        
        # Send via Africa's Talking based on message type
        logger.info(f"Sending {message.message_type} message {message_id} to {message.recipient_phone}")
        
        if message.message_type == 'sms':
            result = services.send_sms(
                recipient=message.recipient_phone,
                message=message.content
            )
        elif message.message_type == 'whatsapp':
            result = services.send_whatsapp(
                recipient=message.recipient_phone,
                message=message.content,
                template_name=message.template.name if message.template else None
            )
        else:
            raise ValueError(f"Unsupported message type: {message.message_type}")
        
        if result['success']:
            # Extract cost as decimal (Africa's Talking returns "RWF 10", extract "10")
            cost_str = result.get('cost', '0')
            if isinstance(cost_str, str) and ' ' in cost_str:
                # Extract number from "RWF 10" format
                cost = cost_str.split()[-1]
            else:
                cost = cost_str
            
            # Update message status
            message.status = "sent"
            message.sent_at = timezone.now()
            message.save()
            
            # Create success log
            MessageLog.objects.create(
                message=message,
                status="sent",
                provider_message_id=result.get('message_id'),
                provider_response=result,
                cost=cost,
                currency="RWF",  # Rwanda Francs
            )
            
            logger.info(f"Successfully sent message {message_id}")
            return {
                "status": "success",
                "message_id": message_id,
                "provider_message_id": result.get('message_id'),
            }
        else:
            raise Exception(result.get('error', 'Failed to send message'))
            
    except Message.DoesNotExist:
        logger.error(f"Message {message_id} not found")
        return {"status": "error", "message": "Message not found"}
        
    except Exception as exc:
        logger.error(f"Error sending message {message_id}: {exc}")
        
        # Update message status to failed
        try:
            message = Message.objects.get(id=message_id)
            message.status = "failed"
            message.save()
            
            # Create failure log
            MessageLog.objects.create(
                message=message,
                status="failed",
                error_message=str(exc),
            )
        except Exception as log_exc:
            logger.error(f"Error creating failure log: {log_exc}")
        
        # Retry the task
        raise self.retry(exc=exc)


@shared_task
def process_message_queue():
    """
    Process pending messages in the queue.
    
    This task runs periodically (every 5 minutes) and:
    1. Finds all pending queue entries with scheduled_time <= now
    2. Creates Message objects for each entry
    3. Triggers send_message_task for each message
    4. Updates queue entry status
    
    Returns:
        dict: Summary of processed messages
    """
    from apps.messaging.models import MessageQueue, Message
    
    # Get pending entries that are due
    now = timezone.now()
    pending_entries = MessageQueue.objects.filter(
        status="pending",
        scheduled_time__lte=now
    ).select_related('appointment', 'appointment__patient')[:100]  # Process 100 at a time
    
    processed_count = 0
    failed_count = 0
    
    for entry in pending_entries:
        try:
            # Update status to processing
            entry.status = "processing"
            entry.save()
            
            # Determine recipient patient
            recipient_patient = None
            if entry.appointment:
                recipient_patient = entry.appointment.patient
            
            # Create message
            message = Message.objects.create(
                recipient_patient=recipient_patient,
                recipient_phone=entry.recipient_phone,
                message_type=entry.message_type,
                content=entry.content,
                status="queued",
            )
            
            # Link message to queue entry
            entry.sent_message = message
            entry.status = "completed"
            entry.processed_at = timezone.now()
            entry.save()
            
            # Trigger async send task
            send_message_task.delay(message.id)
            
            processed_count += 1
            logger.info(f"Processed queue entry {entry.id}, created message {message.id}")
            
        except Exception as exc:
            logger.error(f"Error processing queue entry {entry.id}: {exc}")
            entry.status = "failed"
            entry.error_message = str(exc)
            entry.save()
            failed_count += 1
    
    logger.info(
        f"Queue processing complete: {processed_count} processed, {failed_count} failed"
    )
    
    return {
        "processed": processed_count,
        "failed": failed_count,
        "total": processed_count + failed_count,
    }


@shared_task
def retry_failed_messages():
    """
    Retry messages that failed to send.
    
    This task runs periodically (every 15 minutes) and:
    1. Finds messages with status='failed'
    2. Checks if they haven't exceeded max retries
    3. Re-triggers send_message_task
    
    Returns:
        dict: Summary of retry attempts
    """
    from apps.messaging.models import Message, MessageQueue
    
    # Find failed messages from last 24 hours
    cutoff_time = timezone.now() - timedelta(hours=24)
    failed_messages = Message.objects.filter(
        status="failed",
        created_at__gte=cutoff_time
    )[:50]  # Retry 50 at a time
    
    retry_count = 0
    
    for message in failed_messages:
        try:
            # Check if there's a queue entry with retry logic
            queue_entry = MessageQueue.objects.filter(
                sent_message=message,
                status="failed",
                retry_count__lt=F('max_retries')
            ).first()
            
            if queue_entry:
                # Use queue retry logic
                queue_entry.retry_count += 1
                queue_entry.status = "pending"
                queue_entry.error_message = None
                queue_entry.save()
                
                # Reset message status
                message.status = "queued"
                message.save()
                
                # Trigger send task
                send_message_task.delay(message.id)
                retry_count += 1
                logger.info(f"Retrying message {message.id} (attempt {queue_entry.retry_count})")
            else:
                # No queue entry or max retries exceeded, just retry once
                message.status = "queued"
                message.save()
                send_message_task.delay(message.id)
                retry_count += 1
                logger.info(f"Retrying message {message.id} (no queue entry)")
                
        except Exception as exc:
            logger.error(f"Error retrying message {message.id}: {exc}")
    
    logger.info(f"Retry task complete: {retry_count} messages queued for retry")
    
    return {
        "retried": retry_count,
    }


@shared_task
def send_bulk_messages(recipients, message_type, content, template_id=None):
    """
    Send messages to multiple recipients asynchronously.
    
    Args:
        recipients: List of dicts with 'patient' and 'phone' keys
        message_type: Type of message ('sms' or 'whatsapp')
        content: Message content
        template_id: Optional template ID
        
    Returns:
        dict: Summary of messages created
    """
    from apps.messaging.models import Message
    
    created_count = 0
    
    for recipient in recipients:
        try:
            message = Message.objects.create(
                recipient_patient_id=recipient.get("patient"),
                recipient_phone=recipient["phone"],
                message_type=message_type,
                content=content,
                template_id=template_id,
                status="queued",
            )
            
            # Trigger async send
            send_message_task.delay(message.id)
            created_count += 1
            
        except Exception as exc:
            logger.error(f"Error creating bulk message for {recipient}: {exc}")
    
    logger.info(f"Bulk send complete: {created_count} messages created")
    
    return {
        "created": created_count,
        "total": len(recipients),
    }


@shared_task
def schedule_appointment_reminders(appointment_ids, reminder_times):
    """
    Schedule reminders for multiple appointments.
    
    Args:
        appointment_ids: List of appointment IDs
        reminder_times: List of reminder times (e.g., ['24h', '2h'])
        
    Returns:
        dict: Summary of reminders scheduled
    """
    from apps.messaging.models import MessageQueue, MessageTemplate
    from apps.appointments.models import Appointment
    
    created_count = 0
    
    # Get appointment reminder template
    template = MessageTemplate.objects.filter(
        template_type="appointment_reminder",
        is_active=True
    ).first()
    
    if not template:
        logger.error("No active appointment reminder template found")
        return {"created": 0, "error": "No template found"}
    
    appointments = Appointment.objects.filter(
        id__in=appointment_ids
    ).select_related('patient', 'hospital')
    
    for appointment in appointments:
        for reminder_time in reminder_times:
            try:
                # Calculate scheduled time
                if reminder_time == "24h":
                    scheduled_time = appointment.appointment_datetime - timedelta(hours=24)
                elif reminder_time == "2h":
                    scheduled_time = appointment.appointment_datetime - timedelta(hours=2)
                else:
                    continue
                
                # Skip if scheduled time is in the past
                if scheduled_time < timezone.now():
                    continue
                
                # Prepare message content
                content = template.content_english.format(
                    patient_name=appointment.patient.full_name,
                    date=appointment.appointment_datetime.strftime("%Y-%m-%d"),
                    time=appointment.appointment_datetime.strftime("%H:%M"),
                    hospital=appointment.hospital.name,
                )
                
                # Create queue entry
                MessageQueue.objects.create(
                    recipient_phone=appointment.patient.phone_number,
                    message_type="sms",  # Default to SMS
                    content=content,
                    scheduled_time=scheduled_time,
                    template_name=template.name,
                    appointment=appointment,
                    priority="high",
                    context_data={
                        "appointment_id": appointment.id,
                        "reminder_time": reminder_time,
                    }
                )
                
                created_count += 1
                logger.info(
                    f"Scheduled {reminder_time} reminder for appointment {appointment.id}"
                )
                
            except Exception as exc:
                logger.error(
                    f"Error scheduling reminder for appointment {appointment.id}: {exc}"
                )
    
    logger.info(f"Scheduled {created_count} appointment reminders")
    
    return {
        "created": created_count,
        "appointments": len(appointments),
    }


# Import F for retry_failed_messages
from django.db.models import F
