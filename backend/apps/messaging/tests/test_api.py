"""Tests for messaging API endpoints."""

import pytest
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue
from apps.messaging.tests.factories import (
    MessageTemplateFactory,
    MessageFactory,
    MessageLogFactory,
    MessageQueueFactory,
)
from apps.patients.tests.factories import PatientFactory
from apps.appointments.tests.factories import AppointmentFactory


@pytest.mark.django_db
class TestMessageTemplateAPI:
    """Tests for MessageTemplate API endpoints."""

    def test_list_message_templates(self, authenticated_client):
        """Test listing message templates."""
        MessageTemplateFactory.create_batch(3)
        response = authenticated_client.get("/api/v1/message-templates/")
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_create_message_template(self, authenticated_client):
        """Test creating a message template."""
        data = {
            "name": "test_template",
            "template_type": "appointment_reminder",
            "message_type": "sms",
            "content_english": "Test content",
            "is_active": True,
        }
        response = authenticated_client.post("/api/v1/message-templates/", data)
        assert response.status_code == 201
        assert response.data["name"] == "test_template"

    def test_retrieve_message_template(self, authenticated_client):
        """Test retrieving a single message template."""
        template = MessageTemplateFactory()
        response = authenticated_client.get(f"/api/v1/message-templates/{template.id}/")
        assert response.status_code == 200
        assert response.data["name"] == template.name

    def test_update_message_template(self, authenticated_client):
        """Test updating a message template."""
        template = MessageTemplateFactory()
        data = {"is_active": False}
        response = authenticated_client.patch(f"/api/v1/message-templates/{template.id}/", data)
        assert response.status_code == 200
        assert response.data["is_active"] is False

    def test_filter_templates_by_type(self, authenticated_client):
        """Test filtering templates by template_type."""
        MessageTemplateFactory(template_type="appointment_reminder")
        MessageTemplateFactory(template_type="medication_reminder")
        response = authenticated_client.get("/api/v1/message-templates/?template_type=appointment_reminder")
        assert response.status_code == 200
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestMessageAPI:
    """Tests for Message API endpoints."""

    def test_list_messages(self, authenticated_client):
        """Test listing messages."""
        MessageFactory.create_batch(5)
        response = authenticated_client.get("/api/v1/messages/")
        assert response.status_code == 200
        assert response.data["count"] == 5

    def test_create_message(self, authenticated_client):
        """Test creating a message."""
        patient = PatientFactory()
        template = MessageTemplateFactory()
        data = {
            "recipient_patient": patient.id,
            "recipient_phone": "+250788123456",
            "message_type": "sms",
            "template": template.id,
            "content": "Test message",
            "status": "pending",
        }
        response = authenticated_client.post("/api/v1/messages/", data)
        assert response.status_code == 201
        assert response.data["content"] == "Test message"

    def test_retrieve_message(self, authenticated_client):
        """Test retrieving a single message."""
        message = MessageFactory()
        response = authenticated_client.get(f"/api/v1/messages/{message.id}/")
        assert response.status_code == 200
        assert "patient" in response.data
        assert "template" in response.data

    def test_filter_messages_by_status(self, authenticated_client):
        """Test filtering messages by status."""
        MessageFactory(status="sent")
        MessageFactory(status="pending")
        MessageFactory(status="failed")
        response = authenticated_client.get("/api/v1/messages/?status=sent")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_filter_messages_by_patient(self, authenticated_client):
        """Test filtering messages by patient."""
        patient = PatientFactory()
        MessageFactory.create_batch(3, recipient_patient=patient)
        MessageFactory()  # Different patient
        response = authenticated_client.get(f"/api/v1/messages/?recipient_patient={patient.id}")
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_send_message_action(self, authenticated_client):
        """Test custom send action for queued messages."""
        message = MessageFactory(status="pending", message_type="sms")
        
        # Mock Celery task and Africa's Talking service
        with patch('apps.messaging.views.send_message_task') as mock_task:
            mock_task.delay.return_value.id = 'test-task-id'
            
            response = authenticated_client.post(f"/api/v1/messages/{message.id}/send/")
            
        assert response.status_code == 202  # Now returns 202 with async
        assert 'task_id' in response.data
        
        # Status should be queued for async processing
        message.refresh_from_db()
        assert message.status == "queued"

    def test_send_message_action_already_processed(self, authenticated_client):
        """Test send action for already processed message returns error."""
        message = MessageFactory(status="sent", message_type="sms")
        
        response = authenticated_client.post(f"/api/v1/messages/{message.id}/send/")
        
        assert response.status_code == 400
        assert 'error' in response.data
        assert "already been processed" in response.data['error']

    def test_get_serializer_class_default(self, authenticated_client):
        """Test that get_serializer_class returns default serializer for custom actions."""
        from apps.messaging.views import MessageViewSet
        from apps.messaging.serializers import MessageSerializer
        
        viewset = MessageViewSet()
        viewset.action = 'send'  # Custom action not in explicit list
        serializer_class = viewset.get_serializer_class()
        
        assert serializer_class == MessageSerializer


@pytest.mark.django_db
class TestMessageLogAPI:
    """Tests for MessageLog API endpoints."""

    def test_list_message_logs(self, authenticated_client):
        """Test listing message logs."""
        MessageLogFactory.create_batch(4)
        response = authenticated_client.get("/api/v1/message-logs/")
        assert response.status_code == 200
        assert response.data["count"] == 4

    def test_retrieve_message_log(self, authenticated_client):
        """Test retrieving a single message log."""
        log = MessageLogFactory()
        response = authenticated_client.get(f"/api/v1/message-logs/{log.id}/")
        assert response.status_code == 200
        assert response.data["status"] == log.status

    def test_filter_logs_by_status(self, authenticated_client):
        """Test filtering logs by status."""
        MessageLogFactory(status="delivered")
        MessageLogFactory(status="failed")
        response = authenticated_client.get("/api/v1/message-logs/?status=delivered")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_message_log_readonly(self, authenticated_client):
        """Test that message logs cannot be created via API."""
        message = MessageFactory()
        data = {
            "message": message.id,
            "status": "sent",
            "provider_message_id": "TEST-123",
        }
        response = authenticated_client.post("/api/v1/message-logs/", data)
        assert response.status_code == 405  # Method not allowed


@pytest.mark.django_db
class TestMessageQueueAPI:
    """Tests for MessageQueue API endpoints."""

    def test_list_queue_entries(self, authenticated_client):
        """Test listing queue entries."""
        MessageQueueFactory.create_batch(5)
        response = authenticated_client.get("/api/v1/message-queue/")
        assert response.status_code == 200
        assert response.data["count"] == 5

    def test_create_queue_entry(self, authenticated_client):
        """Test creating a queue entry."""
        patient = PatientFactory()
        appointment = AppointmentFactory(patient=patient)
        scheduled_time = timezone.now() + timedelta(hours=24)
        data = {
            "recipient_phone": "+250788123456",
            "message_type": "sms",
            "content": "Appointment reminder",
            "scheduled_time": scheduled_time.isoformat(),
            "appointment": appointment.id,
            "priority": "high",
            "status": "pending",
        }
        response = authenticated_client.post("/api/v1/message-queue/", data)
        assert response.status_code == 201
        assert response.data["priority"] == "high"

    def test_filter_queue_by_status(self, authenticated_client):
        """Test filtering queue by status."""
        MessageQueueFactory(status="pending")
        MessageQueueFactory(status="completed")
        MessageQueueFactory(status="failed")
        response = authenticated_client.get("/api/v1/message-queue/?status=pending")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_filter_queue_by_priority(self, authenticated_client):
        """Test filtering queue by priority."""
        MessageQueueFactory(priority="urgent")
        MessageQueueFactory(priority="normal")
        response = authenticated_client.get("/api/v1/message-queue/?priority=urgent")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_process_queue_action(self, authenticated_client):
        """Test custom process action for pending queue entries."""
        patient = PatientFactory()
        appointment = AppointmentFactory(patient=patient)
        scheduled_time = timezone.now() - timedelta(hours=1)  # Past due
        entry = MessageQueueFactory(
            status="pending",
            scheduled_time=scheduled_time,
            appointment=appointment,
        )
        response = authenticated_client.post(f"/api/v1/message-queue/{entry.id}/process/")
        assert response.status_code == 200
        entry.refresh_from_db()
        assert entry.status in ["processing", "completed", "failed"]

    def test_process_queue_action_not_pending(self, authenticated_client):
        """Test process action on non-pending entry returns error."""
        entry = MessageQueueFactory(status="completed")
        response = authenticated_client.post(f"/api/v1/message-queue/{entry.id}/process/")
        assert response.status_code == 400
        assert 'error' in response.data
        assert 'not pending' in response.data['error']

    def test_process_queue_action_not_yet_scheduled(self, authenticated_client):
        """Test process action on future-scheduled entry returns error."""
        scheduled_time = timezone.now() + timedelta(hours=1)  # Future
        entry = MessageQueueFactory(status="pending", scheduled_time=scheduled_time)
        response = authenticated_client.post(f"/api/v1/message-queue/{entry.id}/process/")
        assert response.status_code == 400
        assert 'error' in response.data
        assert 'not arrived yet' in response.data['error']

    def test_retry_failed_message(self, authenticated_client):
        """Test retry action for failed messages."""
        entry = MessageQueueFactory(status="failed", retry_count=1)
        response = authenticated_client.post(f"/api/v1/message-queue/{entry.id}/retry/")
        assert response.status_code == 200
        entry.refresh_from_db()
        assert entry.retry_count == 2
        assert entry.status == "pending"
    
    def test_retry_non_failed_message(self, authenticated_client):
        """Test retry action on non-failed message."""
        entry = MessageQueueFactory(status="pending")
        response = authenticated_client.post(f"/api/v1/message-queue/{entry.id}/retry/")
        assert response.status_code == 400
        assert 'Entry is not failed' in response.data['error']
    
    def test_retry_max_retries_reached(self, authenticated_client):
        """Test retry action when max retries reached."""
        entry = MessageQueueFactory(status="failed", retry_count=3, max_retries=3)
        response = authenticated_client.post(f"/api/v1/message-queue/{entry.id}/retry/")
        assert response.status_code == 400
        assert 'Maximum retries reached' in response.data['error']


@pytest.mark.django_db
class TestMessageStatisticsAPI:
    """Tests for message statistics endpoints."""

    def test_get_message_statistics(self, authenticated_client):
        """Test retrieving message statistics."""
        MessageFactory(status="sent")
        MessageFactory(status="delivered")
        MessageFactory(status="failed")
        MessageFactory(status="pending")
        
        response = authenticated_client.get("/api/v1/messages/statistics/")
        assert response.status_code == 200
        assert "total_messages" in response.data
        assert "by_status" in response.data
        assert response.data["by_status"]["sent"] == 1
        assert response.data["by_status"]["failed"] == 1

    def test_get_template_usage_statistics(self, authenticated_client):
        """Test template usage statistics."""
        template1 = MessageTemplateFactory(name="template1")
        template2 = MessageTemplateFactory(name="template2")
        MessageFactory.create_batch(3, template=template1)
        MessageFactory.create_batch(2, template=template2)
        
        response = authenticated_client.get("/api/v1/message-templates/usage_stats/")
        assert response.status_code == 200
        assert len(response.data) >= 2


@pytest.mark.django_db
class TestBulkMessagingAPI:
    """Tests for bulk messaging operations."""

    def test_send_bulk_messages(self, authenticated_client):
        """Test sending messages to multiple recipients."""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        template = MessageTemplateFactory()
        
        data = {
            "recipients": [
                {"patient": patient1.id, "phone": patient1.phone_number},
                {"patient": patient2.id, "phone": patient2.phone_number},
            ],
            "message_type": "sms",
            "template": template.id,
            "content": "Bulk message test",
        }
        response = authenticated_client.post("/api/v1/messages/send_bulk/", data, format="json")
        assert response.status_code == 200
        assert "task_id" in response.data
        assert "recipient_count" in response.data
        assert response.data["recipient_count"] == 2
        assert "message" in response.data

    def test_send_bulk_messages_missing_parameters(self, authenticated_client):
        """Test send bulk with missing required parameters."""
        # Missing recipients
        response = authenticated_client.post("/api/v1/messages/send_bulk/", {
            "message_type": "sms",
            "content": "Test"
        }, format="json")
        assert response.status_code == 400
        assert 'error' in response.data
        assert 'required' in response.data['error']

    def test_schedule_bulk_reminders(self, authenticated_client):
        """Test scheduling bulk appointment reminders."""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        appointment1 = AppointmentFactory(patient=patient1)
        appointment2 = AppointmentFactory(patient=patient2)
        
        data = {
            "appointments": [appointment1.id, appointment2.id],
            "reminder_type": "24h_before",
            "message_type": "whatsapp",
        }
        response = authenticated_client.post("/api/v1/message-queue/schedule_reminders/", data, format="json")
        assert response.status_code == 200
        assert "task_id" in response.data
        assert "appointment_count" in response.data
        assert response.data["appointment_count"] == 2
        assert "message" in response.data
    
    def test_schedule_bulk_reminders_missing_appointments(self, authenticated_client):
        """Test schedule reminders with missing appointments list."""
        response = authenticated_client.post("/api/v1/message-queue/schedule_reminders/", {
            "reminder_type": "24h_before"
        }, format="json")
        assert response.status_code == 400
        assert 'appointments list is required' in response.data['error']
