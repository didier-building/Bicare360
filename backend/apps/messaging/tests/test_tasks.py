"""
Tests for Celery tasks in the messaging app.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from apps.messaging.tasks import (
    send_message_task,
    process_message_queue,
    retry_failed_messages,
    send_bulk_messages,
    schedule_appointment_reminders,
)
from apps.messaging.models import Message, MessageQueue, MessageLog, MessageTemplate
from apps.messaging.tests.factories import (
    MessageFactory,
    MessageQueueFactory,
    MessageTemplateFactory,
)
from apps.appointments.tests.factories import AppointmentFactory
from apps.patients.tests.factories import PatientFactory


@pytest.mark.django_db
class TestSendMessageTask:
    """Test send_message_task."""
    
    @patch('apps.messaging.sms_service.AfricasTalkingService.send_sms')
    def test_send_message_success(self, mock_send_sms):
        """Test successful message sending."""
        # Mock successful SMS sending
        mock_send_sms.return_value = {
            'success': True,
            'response': [{'Status': 'Success', 'MessageId': 'msg123'}]
        }
        
        message = MessageFactory(status="queued", message_type="sms")
        
        result = send_message_task(message.id)
        
        # Verify result
        assert result["status"] == "success"
        assert result["message_id"] == message.id
        
        # Refresh from DB to get updated status
        message.refresh_from_db()
        assert message.status == "sent"
        assert message.sent_at is not None
        
        # Verify log created
        assert MessageLog.objects.filter(message=message, status="sent").exists()
        
        # Verify service was called
        mock_send_sms.assert_called_once()
    
    def test_send_message_not_found(self):
        """Test sending non-existent message."""
        with pytest.raises(Exception):
            send_message_task(99999)
    
    @patch('apps.messaging.sms_service.AfricasTalkingService.send_sms')
    def test_send_message_with_exception(self, mock_send_sms):
        """Test message sending with exception."""
        # Mock SMS service to raise exception
        mock_send_sms.side_effect = Exception("Network error")
        
        message = MessageFactory(status="queued", message_type="sms")
        
        with pytest.raises(Exception):
            send_message_task.apply(args=[message.id], throw=True)

    @patch('apps.messaging.sms_service.MessageService.send_message')
    def test_send_whatsapp_message(self, mock_send):
        """Test sending WhatsApp message."""
        mock_send.return_value = True
        
        template = MessageTemplateFactory(message_type='whatsapp')
        message = MessageFactory(
            status="queued",
            message_type="whatsapp",
            template=template
        )
        
        result = send_message_task(message.id)
        
        assert result["status"] == "success"
        
        # Verify service was called with correct message ID
        mock_send.assert_called_once_with(message.id)


class TestProcessMessageQueue:
    """Test process_message_queue task."""
    
    def test_process_pending_entries(self):
        """Test processing pending queue entries."""
        # Create past scheduled entries
        appointment = AppointmentFactory()
        past_time = timezone.now() - timedelta(minutes=10)
        
        entry1 = MessageQueueFactory(
            status="pending",
            scheduled_time=past_time,
            appointment=appointment
        )
        entry2 = MessageQueueFactory(
            status="pending",
            scheduled_time=past_time,
            appointment=appointment
        )
        
        # Create future entry (should not be processed)
        future_time = timezone.now() + timedelta(hours=1)
        entry3 = MessageQueueFactory(
            status="pending",
            scheduled_time=future_time,
            appointment=appointment
        )
        
        with patch('apps.messaging.tasks.send_message_task.delay') as mock_send:
            result = process_message_queue()
        
        # Verify result
        assert result["processed"] == 2
        assert result["failed"] == 0
        
        # Verify entries updated
        entry1.refresh_from_db()
        assert entry1.status == "completed"
        assert entry1.sent_message is not None
        assert entry1.processed_at is not None
        
        entry2.refresh_from_db()
        assert entry2.status == "completed"
        
        # Verify future entry not processed
        entry3.refresh_from_db()
        assert entry3.status == "pending"
        
        # Verify send tasks triggered
        assert mock_send.call_count == 2
    
    def test_process_empty_queue(self):
        """Test processing when queue is empty."""
        result = process_message_queue()
        
        assert result["processed"] == 0
        assert result["failed"] == 0
    
    def test_process_with_failure(self):
        """Test processing with entry that fails."""
        past_time = timezone.now() - timedelta(minutes=10)
        # Create appointment to avoid IntegrityError
        appointment = AppointmentFactory()
        entry = MessageQueueFactory(
            status="pending",
            scheduled_time=past_time,
            appointment=appointment,
            recipient_phone="+250788123456"
        )
        
        # Mock message creation to fail
        with patch.object(Message.objects, 'create', side_effect=Exception("Test error")):
            result = process_message_queue()
        
        # Verify failed
        assert result["failed"] == 1
        
        # Verify entry marked as failed
        entry.refresh_from_db()
        assert entry.status == "failed"
        assert entry.error_message is not None


@pytest.mark.django_db
class TestRetryFailedMessages:
    """Test retry_failed_messages task."""
    
    def test_retry_failed_message_with_queue(self):
        """Test retrying failed message with queue entry."""
        appointment = AppointmentFactory()
        message = MessageFactory(status="failed")
        queue_entry = MessageQueueFactory(
            sent_message=message,
            status="failed",
            retry_count=0,
            max_retries=3,
            appointment=appointment
        )
        
        with patch('apps.messaging.tasks.send_message_task.delay') as mock_send:
            result = retry_failed_messages()
        
        # Verify retried
        assert result["retried"] == 1
        
        # Verify queue entry updated
        queue_entry.refresh_from_db()
        assert queue_entry.status == "pending"
        assert queue_entry.retry_count == 1
        assert queue_entry.error_message is None
        
        # Verify message reset
        message.refresh_from_db()
        assert message.status == "queued"
        
        # Verify send task triggered
        mock_send.assert_called_once_with(message.id)
    
    def test_retry_max_retries_exceeded(self):
        """Test not retrying when max retries exceeded."""
        appointment = AppointmentFactory()
        patient = PatientFactory()
        
        # Create message with patient
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone=patient.phone_number,
            message_type="sms",
            content="Test",
            status="failed"
        )
        
        queue_entry = MessageQueueFactory(
            sent_message=message,
            status="failed",
            retry_count=3,
            max_retries=3,
            appointment=appointment
        )
        
        with patch('apps.messaging.tasks.send_message_task.delay') as mock_send:
            result = retry_failed_messages()
        
        # Verify not retried (should be 0 since max retries exceeded)
        # Note: task might still retry messages without queue entry, so check the queue entry specifically
        queue_entry.refresh_from_db()
        assert queue_entry.status == "failed"
        assert queue_entry.retry_count == 3
    
    def test_retry_old_messages_not_included(self):
        """Test that old failed messages are not retried."""
        from django.utils import timezone as tz
        old_time = tz.now() - timedelta(hours=48)
        
        # Create the message with an old timestamp
        message = Message.objects.create(
            recipient_patient=PatientFactory(),
            recipient_phone="+250788123456",
            message_type="sms",
            content="Test",
            status="failed"
        )
        # Manually update created_at to bypass auto_now_add
        Message.objects.filter(id=message.id).update(created_at=old_time)
        message.refresh_from_db()
        
        with patch('apps.messaging.tasks.send_message_task.delay') as mock_send:
            result = retry_failed_messages()
        
        # Verify not retried
        assert result["retried"] == 0
        mock_send.assert_not_called()


@pytest.mark.django_db
class TestSendBulkMessages:
    """Test send_bulk_messages task."""
    
    def test_send_bulk_success(self):
        """Test sending bulk messages successfully."""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        
        recipients = [
            {"patient": patient1.id, "phone": patient1.phone_number},
            {"patient": patient2.id, "phone": patient2.phone_number},
        ]
        
        with patch('apps.messaging.tasks.send_message_task.delay') as mock_send:
            result = send_bulk_messages(
                recipients=recipients,
                message_type="sms",
                content="Test message"
            )
        
        # Verify result
        assert result["created"] == 2
        assert result["total"] == 2
        
        # Verify messages created
        assert Message.objects.filter(status="queued").count() == 2
        
        # Verify send tasks triggered
        assert mock_send.call_count == 2
    
    def test_send_bulk_with_template(self):
        """Test bulk sending with template."""
        template = MessageTemplateFactory()
        patient = PatientFactory()
        
        recipients = [{"patient": patient.id, "phone": patient.phone_number}]
        
        with patch('apps.messaging.tasks.send_message_task.delay'):
            result = send_bulk_messages(
                recipients=recipients,
                message_type="sms",
                content="Test",
                template_id=template.id
            )
        
        # Verify message has template
        message = Message.objects.first()
        assert message.template == template


@pytest.mark.django_db
class TestTaskIntegration:
    """Test task integration scenarios."""
    
    @patch('apps.messaging.sms_service.AfricasTalkingService.send_sms')
    def test_full_queue_processing_flow(self, mock_send_sms):
        """Test complete flow from queue to sent message."""
        # Mock successful SMS sending
        mock_send_sms.return_value = {
            'success': True,
            'response': [{'Status': 'Success', 'MessageId': 'msg123'}]
        }
        
        # Create queue entry
        appointment = AppointmentFactory()
        past_time = timezone.now() - timedelta(minutes=5)
        entry = MessageQueueFactory(
            status="pending",
            scheduled_time=past_time,
            appointment=appointment,
            message_type="sms"
        )
        
        # Process queue
        with patch('apps.messaging.tasks.send_message_task.delay') as mock_send:
            queue_result = process_message_queue()
        
        assert queue_result["processed"] == 1
        
        # Verify message created
        entry.refresh_from_db()
        assert entry.sent_message is not None
        message = entry.sent_message
        
        # Send message
        send_result = send_message_task(message.id)
        
        assert send_result["status"] == "success"
        
        # Verify complete
        message.refresh_from_db()
        assert message.status == "sent"
        assert MessageLog.objects.filter(message=message).exists()
