"""Tests for messaging serializers."""

import pytest
from django.utils import timezone
from datetime import timedelta
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue
from apps.messaging.serializers import (
    MessageTemplateSerializer,
    MessageSerializer,
    MessageListSerializer,
    MessageDetailSerializer,
    MessageCreateSerializer,
    MessageLogSerializer,
    MessageQueueSerializer,
)
from apps.patients.tests.factories import PatientFactory
from apps.appointments.tests.factories import AppointmentFactory


@pytest.mark.django_db
class TestMessageTemplateSerializer:
    """Tests for the MessageTemplateSerializer."""

    def test_serialize_message_template(self):
        """Test serializing a message template."""
        template = MessageTemplate.objects.create(
            name="appointment_reminder_24h",
            template_type="appointment_reminder",
            message_type="sms",
            content_english="Hello {patient_name}, you have an appointment on {appointment_date}.",
            content_kinyarwanda="Muraho {patient_name}, ufite gahunda yo {appointment_date}.",
            is_active=True,
        )
        serializer = MessageTemplateSerializer(template)
        data = serializer.data
        
        assert data["name"] == "appointment_reminder_24h"
        assert data["template_type"] == "appointment_reminder"
        assert data["message_type"] == "sms"
        assert "{patient_name}" in data["content_english"]
        assert data["is_active"] is True
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_message_template_via_serializer(self):
        """Test creating a message template via serializer."""
        data = {
            "name": "test_template",
            "template_type": "general_notification",
            "message_type": "whatsapp",
            "content_english": "Test message content",
            "is_active": True,
        }
        serializer = MessageTemplateSerializer(data=data)
        assert serializer.is_valid()
        template = serializer.save()
        assert template.name == "test_template"
        assert template.template_type == "general_notification"


@pytest.mark.django_db
class TestMessageSerializer:
    """Tests for the MessageSerializer."""

    def test_serialize_message(self):
        """Test serializing a message."""
        patient = PatientFactory()
        template = MessageTemplate.objects.create(
            name="test_template",
            template_type="general_notification",
            message_type="sms",
            content_english="Test content",
        )
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            template=template,
            content="Hello John Doe",
            status="sent",
        )
        serializer = MessageSerializer(message)
        data = serializer.data
        
        assert data["recipient_phone"] == "+250788123456"
        assert data["message_type"] == "sms"
        assert data["content"] == "Hello John Doe"
        assert data["status"] == "sent"
        assert "created_at" in data

    def test_create_message_via_serializer(self):
        """Test creating a message via serializer."""
        patient = PatientFactory()
        data = {
            "recipient_patient": patient.id,
            "recipient_phone": "+250788123456",
            "message_type": "sms",
            "content": "Test message",
            "status": "pending",
        }
        serializer = MessageCreateSerializer(data=data)
        assert serializer.is_valid()
        message = serializer.save()
        assert message.recipient_phone == "+250788123456"
        assert message.status == "pending"


@pytest.mark.django_db
class TestMessageListSerializer:
    """Tests for the MessageListSerializer."""

    def test_message_list_serializer_includes_patient_name(self):
        """Test that list serializer includes patient name."""
        patient = PatientFactory(first_name="John", last_name="Doe")
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="sent",
        )
        serializer = MessageListSerializer(message)
        data = serializer.data
        
        assert data["patient_name"] == "John Doe"
        assert data["recipient_phone"] == "+250788123456"
        assert data["message_type"] == "sms"
        assert data["status"] == "sent"

    def test_message_list_serializer_with_template(self):
        """Test list serializer with template information."""
        patient = PatientFactory()
        template = MessageTemplate.objects.create(
            name="test_template",
            template_type="appointment_reminder",
            message_type="sms",
            content_english="Test",
        )
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            template=template,
            content="Test",
            status="delivered",
        )
        serializer = MessageListSerializer(message)
        data = serializer.data
        
        assert data["template_name"] == "test_template"
        assert data["status"] == "delivered"


@pytest.mark.django_db
class TestMessageDetailSerializer:
    """Tests for the MessageDetailSerializer."""

    def test_message_detail_serializer_includes_nested_data(self):
        """Test that detail serializer includes nested patient and template data."""
        patient = PatientFactory(first_name="Jane", last_name="Smith")
        template = MessageTemplate.objects.create(
            name="reminder_template",
            template_type="medication_reminder",
            message_type="whatsapp",
            content_english="Take your medication",
        )
        appointment = AppointmentFactory(patient=patient)
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="whatsapp",
            template=template,
            appointment=appointment,
            content="Take your medication at 9 AM",
            status="delivered",
        )
        serializer = MessageDetailSerializer(message)
        data = serializer.data
        
        assert "patient" in data
        assert "Jane" in data["patient"]["full_name"]
        assert "Smith" in data["patient"]["full_name"]
        assert "template" in data
        assert data["template"]["name"] == "reminder_template"
        assert "appointment" in data
        assert data["appointment"] is not None


@pytest.mark.django_db
class TestMessageCreateSerializer:
    """Tests for the MessageCreateSerializer."""

    def test_create_message_with_required_fields(self):
        """Test creating a message with only required fields."""
        patient = PatientFactory()
        data = {
            "recipient_patient": patient.id,
            "recipient_phone": "+250788123456",
            "message_type": "sms",
            "content": "Hello world",
            "status": "pending",
        }
        serializer = MessageCreateSerializer(data=data)
        assert serializer.is_valid()
        message = serializer.save()
        assert message.recipient_patient == patient
        assert message.content == "Hello world"

    def test_create_message_with_optional_fields(self):
        """Test creating a message with optional fields."""
        patient = PatientFactory()
        template = MessageTemplate.objects.create(
            name="test", template_type="general_notification", message_type="sms", content_english="Test"
        )
        appointment = AppointmentFactory(patient=patient)
        scheduled_time = timezone.now() + timedelta(hours=1)
        
        data = {
            "recipient_patient": patient.id,
            "recipient_phone": "+250788123456",
            "message_type": "sms",
            "template": template.id,
            "appointment": appointment.id,
            "content": "Test message",
            "status": "queued",
            "scheduled_send_time": scheduled_time.isoformat(),
        }
        serializer = MessageCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        message = serializer.save()
        assert message.template == template
        assert message.appointment == appointment


@pytest.mark.django_db
class TestMessageLogSerializer:
    """Tests for the MessageLogSerializer."""

    def test_serialize_message_log(self):
        """Test serializing a message log."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="sent",
        )
        log = MessageLog.objects.create(
            message=message,
            status="delivered",
            provider_message_id="AT-12345",
            provider_response='{"status": "success"}',
            cost=0.05,
            currency="USD",
        )
        serializer = MessageLogSerializer(log)
        data = serializer.data
        
        assert data["status"] == "delivered"
        assert data["provider_message_id"] == "AT-12345"
        assert data["cost"] == "0.0500"
        assert data["currency"] == "USD"
        assert "timestamp" in data

    def test_message_log_serializer_readonly(self):
        """Test that message log serializer is read-only."""
        patient = PatientFactory()
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="pending",
        )
        log = MessageLog.objects.create(message=message, status="sent")
        serializer = MessageLogSerializer(log)
        
        # Verify read-only fields are present
        assert "message" in serializer.data
        assert "timestamp" in serializer.data


@pytest.mark.django_db
class TestMessageQueueSerializer:
    """Tests for the MessageQueueSerializer."""

    def test_serialize_message_queue(self):
        """Test serializing a queue entry."""
        patient = PatientFactory()
        appointment = AppointmentFactory(patient=patient)
        scheduled_time = timezone.now() + timedelta(hours=24)
        
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Appointment reminder",
            scheduled_time=scheduled_time,
            template_name="appointment_reminder_24h",
            context_data={"patient_name": "John Doe"},
            appointment=appointment,
            priority="high",
            status="pending",
        )
        serializer = MessageQueueSerializer(queue_entry)
        data = serializer.data
        
        assert data["recipient_phone"] == "+250788123456"
        assert data["message_type"] == "sms"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert data["template_name"] == "appointment_reminder_24h"
        assert "context_data" in data

    def test_create_queue_entry_via_serializer(self):
        """Test creating a queue entry via serializer."""
        patient = PatientFactory()
        appointment = AppointmentFactory(patient=patient)
        scheduled_time = timezone.now() + timedelta(hours=2)
        
        data = {
            "recipient_phone": "+250788123456",
            "message_type": "whatsapp",
            "content": "Test reminder",
            "scheduled_time": scheduled_time.isoformat(),
            "appointment": appointment.id,
            "priority": "normal",
            "status": "pending",
        }
        serializer = MessageQueueSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        queue_entry = serializer.save()
        assert queue_entry.priority == "normal"
        assert queue_entry.appointment == appointment

    def test_update_queue_entry_status(self):
        """Test updating queue entry status."""
        scheduled_time = timezone.now() + timedelta(hours=1)
        queue_entry = MessageQueue.objects.create(
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            scheduled_time=scheduled_time,
            status="pending",
        )
        
        data = {"status": "processing"}
        serializer = MessageQueueSerializer(queue_entry, data=data, partial=True)
        assert serializer.is_valid()
        updated_entry = serializer.save()
        assert updated_entry.status == "processing"
