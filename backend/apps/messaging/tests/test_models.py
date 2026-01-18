"""Tests for messaging models."""

import pytest
from django.utils import timezone
from datetime import timedelta
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue
from apps.patients.tests.factories import PatientFactory
from apps.appointments.tests.factories import AppointmentFactory


@pytest.mark.django_db
class TestMessageTemplateModel:
    """Tests for the MessageTemplate model."""

    def test_create_message_template(self):
        """Test creating a message template with required fields."""
        template = MessageTemplate.objects.create(
            name="appointment_reminder_24h",
            template_type="appointment_reminder",
            message_type="sms",
            content_english="Hello {patient_name}, you have an appointment on {appointment_date} at {appointment_time}.",
            content_kinyarwanda="Muraho {patient_name}, ufite gahunda yo {appointment_date} ku isaha {appointment_time}.",
            is_active=True,
        )
        assert template.name == "appointment_reminder_24h"
        assert template.template_type == "appointment_reminder"
        assert template.message_type == "sms"
        assert "{patient_name}" in template.content_english
        assert template.is_active is True

    def test_message_template_string_representation(self):
        """Test the string representation of a message template."""
        template = MessageTemplate.objects.create(
            name="test_template",
            template_type="appointment_reminder",
            message_type="sms",
            content_english="Test content",
        )
        assert str(template) == "test_template (sms)"

    def test_message_template_type_choices(self):
        """Test that template_type choices are valid."""
        template = MessageTemplate.objects.create(
            name="test",
            template_type="medication_reminder",
            message_type="whatsapp",
            content_english="Test",
        )
        assert template.template_type in [
            "appointment_reminder",
            "medication_reminder",
            "general_notification",
            "emergency_alert",
            "survey",
        ]

    def test_message_template_message_type_choices(self):
        """Test that message_type choices are valid."""
        template = MessageTemplate.objects.create(
            name="test",
            template_type="general_notification",
            message_type="whatsapp",
            content_english="Test",
        )
        assert template.message_type in ["sms", "whatsapp"]

    def test_message_template_timestamps(self):
        """Test that timestamps are auto-generated."""
        template = MessageTemplate.objects.create(
            name="test",
            template_type="general_notification",
            message_type="sms",
            content_english="Test",
        )
        assert template.created_at is not None
        assert template.updated_at is not None

    def test_message_template_ordering(self):
        """Test that templates are ordered by name."""
        MessageTemplate.objects.create(
            name="z_template", template_type="general_notification", message_type="sms", content_english="Z"
        )
        MessageTemplate.objects.create(
            name="a_template", template_type="general_notification", message_type="sms", content_english="A"
        )
        templates = MessageTemplate.objects.all()
        assert templates[0].name == "a_template"
        assert templates[1].name == "z_template"


@pytest.mark.django_db
class TestMessageModel:
    """Tests for the Message model."""

    def test_create_message(self):
        """Test creating a message with required fields."""
        patient = PatientFactory()
        template = MessageTemplate.objects.create(
            name="test_template",
            template_type="general_notification",
            message_type="sms",
            content_english="Hello {patient_name}",
        )
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            template=template,
            content="Hello John Doe",
            status="pending",
        )
        assert message.recipient_patient == patient
        assert message.recipient_phone == "+250788123456"
        assert message.message_type == "sms"
        assert message.status == "pending"

    def test_create_message_with_appointment(self):
        """Test creating a message linked to an appointment."""
        patient = PatientFactory()
        appointment = AppointmentFactory(patient=patient)
        template = MessageTemplate.objects.create(
            name="apt_reminder",
            template_type="appointment_reminder",
            message_type="sms",
            content_english="Appointment reminder",
        )
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone=patient.phone_number,
            message_type="sms",
            template=template,
            content="Your appointment is scheduled",
            appointment=appointment,
            status="pending",
        )
        assert message.appointment == appointment
        assert message.recipient_patient == patient

    def test_message_string_representation(self):
        """Test the string representation of a message."""
        patient = PatientFactory(first_name="John", last_name="Doe")
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test message",
            status="sent",
        )
        assert "John Doe" in str(message)
        assert "sms" in str(message)

    def test_message_status_choices(self):
        """Test that status choices are valid."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="delivered",
        )
        assert message.status in ["pending", "queued", "sent", "delivered", "failed", "cancelled"]

    def test_message_cascade_delete_patient(self):
        """Test that deleting a patient cascades to messages."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        message_id = message.id
        patient.delete()
        assert not Message.objects.filter(id=message_id).exists()

    def test_message_set_null_on_template_delete(self):
        """Test that deleting a template sets template field to null."""
        patient = PatientFactory()
        template = MessageTemplate.objects.create(
            name="test", template_type="general_notification", message_type="sms", content_english="Test"
        )
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            template=template,
            content="Test",
            status="pending",
        )
        template.delete()
        message.refresh_from_db()
        assert message.template is None

    def test_message_ordering(self):
        """Test that messages are ordered by created_at descending."""
        patient = PatientFactory()
        message1 = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="First",
            status="pending",
        )
        message2 = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Second",
            status="pending",
        )
        messages = Message.objects.all()
        assert messages[0] == message2
        assert messages[1] == message1

    def test_message_optional_fields(self):
        """Test that optional fields can be null."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        assert message.template is None
        assert message.appointment is None
        assert message.scheduled_send_time is None
        assert message.sent_at is None


@pytest.mark.django_db
class TestMessageLogModel:
    """Tests for the MessageLog model."""

    def test_create_message_log(self):
        """Test creating a message log entry."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        log = MessageLog.objects.create(
            message=message,
            status="sent",
            provider_message_id="AT-12345",
            provider_response='{"status": "success"}',
            cost=0.05,
            currency="USD",
        )
        assert log.message == message
        assert log.status == "sent"
        assert log.provider_message_id == "AT-12345"
        assert log.cost == 0.05

    def test_message_log_string_representation(self):
        """Test the string representation of a message log."""
        patient = PatientFactory(first_name="John", last_name="Doe")
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        log = MessageLog.objects.create(
            message=message, status="delivered", provider_message_id="AT-12345"
        )
        assert "delivered" in str(log).lower()

    def test_message_log_cascade_delete(self):
        """Test that deleting a message cascades to logs."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        log = MessageLog.objects.create(message=message, status="sent")
        log_id = log.id
        message.delete()
        assert not MessageLog.objects.filter(id=log_id).exists()

    def test_message_log_ordering(self):
        """Test that logs are ordered by timestamp descending."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        log1 = MessageLog.objects.create(message=message, status="sent")
        log2 = MessageLog.objects.create(message=message, status="delivered")
        logs = MessageLog.objects.all()
        assert logs[0] == log2
        assert logs[1] == log1

    def test_message_log_optional_fields(self):
        """Test that optional fields can be null."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        log = MessageLog.objects.create(message=message, status="failed")
        assert log.provider_message_id is None
        assert log.provider_response is None
        assert log.error_message is None
        assert log.cost is None


@pytest.mark.django_db
class TestMessageQueueModel:
    """Tests for the MessageQueue model."""

    def test_create_message_queue_entry(self):
        """Test creating a message queue entry."""
        patient = PatientFactory()
        appointment = AppointmentFactory(patient=patient)
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test message",
            scheduled_time=timezone.now() + timedelta(hours=24),
            template_name="appointment_reminder_24h",
            context_data={"patient_name": "John Doe", "appointment_date": "2026-01-20"},
            appointment=appointment,
            priority="high",
        )
        assert queue_entry.recipient_phone == "+250788123456"
        assert queue_entry.message_type == "sms"
        assert queue_entry.priority == "high"
        assert queue_entry.status == "pending"

    def test_message_queue_string_representation(self):
        """Test the string representation of a queue entry."""
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="whatsapp",
            content="Test",
            scheduled_time=timezone.now(),
            priority="normal",
        )
        assert "+250788123456" in str(queue_entry)
        assert "whatsapp" in str(queue_entry)

    def test_message_queue_priority_choices(self):
        """Test that priority choices are valid."""
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            scheduled_time=timezone.now(),
            priority="urgent",
        )
        assert queue_entry.priority in ["low", "normal", "high", "urgent"]

    def test_message_queue_ordering(self):
        """Test that queue entries are ordered by priority and scheduled_time."""
        time_now = timezone.now()
        queue1 = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Normal",
            scheduled_time=time_now,
            priority="normal",
        )
        queue2 = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Urgent",
            scheduled_time=time_now,
            priority="urgent",
        )
        entries = MessageQueue.objects.all()
        # Urgent should come first
        assert entries[0] == queue2
        assert entries[1] == queue1

    def test_message_queue_cascade_delete_appointment(self):
        """Test that deleting an appointment cascades to queue entries."""
        patient = PatientFactory()
        appointment = AppointmentFactory(patient=patient)
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            scheduled_time=timezone.now(),
            appointment=appointment,
        )
        entry_id = queue_entry.id
        appointment.delete()
        assert not MessageQueue.objects.filter(id=entry_id).exists()

    def test_message_queue_optional_fields(self):
        """Test that optional fields can be null."""
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            scheduled_time=timezone.now(),
        )
        assert queue_entry.template_name is None
        assert queue_entry.context_data is None
        assert queue_entry.appointment is None
        assert queue_entry.sent_message is None
        assert queue_entry.processed_at is None
        assert queue_entry.error_message is None

    def test_message_queue_retry_logic(self):
        """Test retry count and max retries."""
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            scheduled_time=timezone.now(),
            retry_count=0,
            max_retries=3,
        )
        assert queue_entry.retry_count == 0
        assert queue_entry.max_retries == 3
        
        # Simulate retry
        queue_entry.retry_count += 1
        queue_entry.save()
        assert queue_entry.retry_count == 1
