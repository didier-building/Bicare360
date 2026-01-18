"""Signal handlers for the messaging app."""

from datetime import timedelta
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender='appointments.Appointment')
def create_appointment_reminders(sender, instance, created, **kwargs):
    """
    Auto-create message queue entries when appointments are scheduled.
    Creates two reminders:
    - 24 hours before appointment
    - 1 hour before appointment
    """
    from apps.messaging.models import MessageQueue, MessageTemplate
    
    # Only create reminders for scheduled/confirmed appointments
    if instance.status not in ['scheduled', 'confirmed']:
        return
    
    # Skip if appointment is in the past
    if instance.appointment_datetime <= timezone.now():
        return
    
    # Check if patient has a phone number
    if not instance.patient.phone_number or instance.patient.phone_number.strip() == "":
        return
    
    # Get or create reminder templates
    template_24h, _ = MessageTemplate.objects.get_or_create(
        name='24h_appointment_reminder',
        defaults={
            'template_type': 'appointment_reminder',
            'message_type': 'sms',
            'content_english': 'Reminder: You have an appointment with {hospital_name} tomorrow at {appointment_time}. Please confirm your attendance.',
            'is_active': True,
        }
    )
    
    template_1h, _ = MessageTemplate.objects.get_or_create(
        name='1h_appointment_reminder',
        defaults={
            'template_type': 'appointment_reminder',
            'message_type': 'sms',
            'content_english': 'Reminder: Your appointment with {hospital_name} is in 1 hour at {appointment_time}. See you soon!',
            'is_active': True,
        }
    )
    
    # Calculate reminder times
    time_24h_before = instance.appointment_datetime - timedelta(hours=24)
    time_1h_before = instance.appointment_datetime - timedelta(hours=1)
    
    # Prepare context data
    context = {
        'hospital_name': instance.hospital.name,
        'appointment_time': instance.appointment_datetime.strftime('%I:%M %p'),
        'appointment_date': instance.appointment_datetime.strftime('%B %d, %Y'),
        'appointment_type': instance.get_appointment_type_display(),
        'appointment_id': instance.id,
    }
    
    # Render content for 24h reminder
    content_24h = template_24h.content_english.format(**context)
    
    # Only create 24h reminder if it's in the future
    if time_24h_before > timezone.now():
        # Check if reminder already exists
        existing_24h = MessageQueue.objects.filter(
            recipient_phone=instance.patient.phone_number,
            template_name=template_24h.name,
            scheduled_time=time_24h_before,
            status__in=['pending', 'processing']
        ).first()
        
        if not existing_24h:
            MessageQueue.objects.create(
                recipient_phone=instance.patient.phone_number,
                message_type='sms',
                content=content_24h,
                scheduled_time=time_24h_before,
                template_name=template_24h.name,
                context_data=context,
                appointment=instance,
                priority='high',
                status='pending',
            )
    
    # Render content for 1h reminder
    content_1h = template_1h.content_english.format(**context)
    
    # Only create 1h reminder if it's in the future
    if time_1h_before > timezone.now():
        # Check if reminder already exists
        existing_1h = MessageQueue.objects.filter(
            recipient_phone=instance.patient.phone_number,
            template_name=template_1h.name,
            scheduled_time=time_1h_before,
            status__in=['pending', 'processing']
        ).first()
        
        if not existing_1h:
            MessageQueue.objects.create(
                recipient_phone=instance.patient.phone_number,
                message_type='sms',
                content=content_1h,
                scheduled_time=time_1h_before,
                template_name=template_1h.name,
                context_data=context,
                appointment=instance,
                priority='high',
                status='pending',
            )


@receiver(pre_delete, sender='appointments.Appointment')
def cancel_appointment_reminders(sender, instance, **kwargs):
    """
    Cancel pending reminders when appointment is deleted.
    """
    from apps.messaging.models import MessageQueue
    
    # Cancel any pending reminders for this appointment
    MessageQueue.objects.filter(
        appointment=instance,
        status__in=['pending', 'processing']
    ).update(status='cancelled')
