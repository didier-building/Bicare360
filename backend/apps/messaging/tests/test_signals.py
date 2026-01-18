"""
Tests for messaging signal handlers.
Tests appointment reminder auto-creation and cancellation.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from apps.messaging.models import MessageQueue, MessageTemplate
from apps.appointments.tests.factories import AppointmentFactory
from apps.patients.tests.factories import PatientFactory
from apps.enrollment.tests.factories import HospitalFactory


@pytest.mark.django_db
class TestAppointmentReminderSignals:
    """Tests for automatic appointment reminder creation."""

    def test_create_reminders_on_appointment_creation(self):
        """Test that reminders are created when appointment is scheduled."""
        # Create appointment 48 hours in the future
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        hospital = HospitalFactory()
        
        appointment = AppointmentFactory(
            patient=patient,
            hospital=hospital,
            appointment_datetime=future_time,
            status='scheduled'
        )
        
        # Check that 2 reminders were created
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 2
        
        # Check 24h reminder
        reminder_24h = reminders.filter(
            template_name='24h_appointment_reminder'
        ).first()
        assert reminder_24h is not None
        assert reminder_24h.scheduled_time == future_time - timedelta(hours=24)
        assert reminder_24h.priority == 'high'
        assert reminder_24h.status == 'pending'
        assert reminder_24h.context_data['appointment_id'] == appointment.id
        assert reminder_24h.context_data['hospital_name'] == hospital.name
        
        # Check 1h reminder
        reminder_1h = reminders.filter(
            template_name='1h_appointment_reminder'
        ).first()
        assert reminder_1h is not None
        assert reminder_1h.scheduled_time == future_time - timedelta(hours=1)
        assert reminder_1h.priority == 'high'

    def test_no_reminders_for_past_appointments(self):
        """Test that no reminders are created for past appointments."""
        past_time = timezone.now() - timedelta(hours=2)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=past_time,
            status='scheduled'
        )
        
        # No reminders should be created
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 0

    def test_no_reminders_for_cancelled_appointments(self):
        """Test that no reminders are created for cancelled appointments."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='cancelled'
        )
        
        # No reminders should be created
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 0

    def test_no_reminders_for_completed_appointments(self):
        """Test that no reminders are created for completed appointments."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='completed'
        )
        
        # No reminders should be created
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 0

    def test_no_reminders_for_patient_without_phone(self):
        """Test that no reminders are created if patient has no phone number."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="")  # Empty phone number
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='scheduled'
        )
        
        # No reminders should be created
        reminders = MessageQueue.objects.all()
        assert reminders.count() == 0

    def test_only_future_reminders_created(self):
        """Test that only reminders in the future are created."""
        # Appointment in 2 hours (24h reminder would be in past)
        future_time = timezone.now() + timedelta(hours=2)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='scheduled'
        )
        
        # Only 1h reminder should be created
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 1
        assert reminders.first().template_name == '1h_appointment_reminder'

    def test_no_duplicate_reminders(self):
        """Test that duplicate reminders are not created for same time slot."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        hospital = HospitalFactory()
        
        # Create first appointment
        appointment1 = AppointmentFactory(
            patient=patient,
            hospital=hospital,
            appointment_datetime=future_time,
            status='scheduled'
        )
        
        # Verify 2 reminders created
        reminders_first = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders_first.count() == 2
        
        # Try to create same appointment again (simulates update)
        # Signal checks for existing reminders at same time
        appointment1.save()  # Re-save triggers signal
        
        # Should still have only 2 reminders (no duplicates)
        reminders_after = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders_after.count() == 2

    def test_reminder_templates_auto_created(self):
        """Test that reminder templates are auto-created if they don't exist."""
        # Clear existing templates
        MessageTemplate.objects.filter(
            name__in=['24h_appointment_reminder', '1h_appointment_reminder']
        ).delete()
        
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='scheduled'
        )
        
        # Check that templates were created
        template_24h = MessageTemplate.objects.filter(
            name='24h_appointment_reminder'
        ).first()
        assert template_24h is not None
        assert template_24h.message_type == 'sms'
        assert template_24h.is_active is True
        
        template_1h = MessageTemplate.objects.filter(
            name='1h_appointment_reminder'
        ).first()
        assert template_1h is not None
        assert template_1h.message_type == 'sms'

    def test_reminder_context_includes_appointment_details(self):
        """Test that reminder context includes all necessary appointment details."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        hospital = HospitalFactory(name="Test Hospital")
        
        appointment = AppointmentFactory(
            patient=patient,
            hospital=hospital,
            appointment_datetime=future_time,
            appointment_type='consultation',
            status='scheduled'
        )
        
        reminder = MessageQueue.objects.first()
        assert reminder is not None
        assert 'appointment_id' in reminder.context_data
        assert 'hospital_name' in reminder.context_data
        assert 'appointment_time' in reminder.context_data
        assert 'appointment_date' in reminder.context_data
        assert 'appointment_type' in reminder.context_data
        assert reminder.context_data['hospital_name'] == 'Test Hospital'
        assert reminder.context_data['appointment_id'] == appointment.id

    def test_cancel_reminders_on_appointment_deletion(self):
        """Test that reminders are cancelled when appointment is deleted."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='scheduled'
        )
        
        # Verify reminders were created
        reminders_before = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number,
            status__in=['pending', 'processing']
        )
        assert reminders_before.count() == 2
        reminder_ids = list(reminders_before.values_list('id', flat=True))
        
        # Delete appointment
        appointment.delete()
        
        # Check that reminders were cancelled (CASCADE deletes them)
        # Since appointment FK has CASCADE, queue entries are deleted not cancelled
        reminders_after = MessageQueue.objects.filter(id__in=reminder_ids)
        assert reminders_after.count() == 0  # They're deleted, not cancelled

    def test_reminders_not_created_for_no_show_appointments(self):
        """Test that no reminders are created for no-show appointments."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='no_show'
        )
        
        # No reminders should be created
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 0

    def test_reminders_created_for_confirmed_appointments(self):
        """Test that reminders are created for confirmed appointments."""
        future_time = timezone.now() + timedelta(hours=48)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='confirmed'
        )
        
        # Reminders should be created
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 2

    def test_appointment_30_minutes_away_no_reminders(self):
        """Test that no reminders are created for appointments less than 1h away."""
        # Appointment in 30 minutes
        future_time = timezone.now() + timedelta(minutes=30)
        patient = PatientFactory(phone_number="+250788123456")
        
        appointment = AppointmentFactory(
            patient=patient,
            appointment_datetime=future_time,
            status='scheduled'
        )
        
        # No reminders should be created (both would be in the past)
        reminders = MessageQueue.objects.filter(
            recipient_phone=patient.phone_number
        )
        assert reminders.count() == 0
