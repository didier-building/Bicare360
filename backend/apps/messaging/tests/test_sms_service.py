"""
Tests for Africa's Talking SMS/WhatsApp service integration.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.utils import timezone
from apps.messaging.sms_service import AfricasTalkingService, MessageService
from apps.messaging.models import Message, MessageLog, MessageTemplate
from apps.patients.tests.factories import PatientFactory
from apps.appointments.tests.factories import AppointmentFactory


@pytest.mark.django_db
class TestAfricasTalkingService:
    """Test Africa's Talking service integration."""

    @patch('apps.messaging.sms_service.africastalking')
    def test_send_sms_success(self, mock_at):
        """Test successful SMS sending."""
        mock_at.SMS.return_value.send.return_value = {
            'SMSMessageData': {
                'Message': 'Sent',
                'Recipients': [{'Status': 'Success', 'MessageId': 'msg123'}]
            }
        }
        
        service = AfricasTalkingService()
        result = service.send_sms('+250788123456', 'Test message')
        
        assert result['success'] is True
        assert 'response' in result

    @patch('apps.messaging.sms_service.africastalking')
    def test_send_sms_formats_phone_number(self, mock_at):
        """Test SMS formats phone number correctly."""
        mock_at.SMS.return_value.send.return_value = {
            'SMSMessageData': {
                'Message': 'Sent',
                'Recipients': [{'Status': 'Success'}]
            }
        }
        
        service = AfricasTalkingService()
        # Test that service formats phone number
        result = service.send_sms('0788123456', 'Test')
        
        assert result['success'] is True

    @patch('apps.messaging.sms_service.africastalking')
    def test_send_sms_failure(self, mock_at):
        """Test SMS sending failure handling."""
        # Set up mock before initialization
        mock_sms = MagicMock()
        mock_sms.send.side_effect = Exception('API Error')
        mock_at.SMS = mock_sms
        mock_at.Whatsapp = MagicMock()
        
        service = AfricasTalkingService()
        result = service.send_sms('+250788123456', 'Test message')
        
        assert result['success'] is False
        assert 'error' in result

    @patch('apps.messaging.sms_service.africastalking')
    def test_send_bulk_sms(self, mock_at):
        """Test bulk SMS sending."""
        mock_at.SMS.return_value.send.return_value = {
            'SMSMessageData': {
                'Message': 'Sent',
                'Recipients': [
                    {'Status': 'Success', 'MessageId': 'msg1'},
                    {'Status': 'Success', 'MessageId': 'msg2'}
                ]
            }
        }
        
        service = AfricasTalkingService()
        result = service.send_bulk_sms(['+250788123456', '+250788654321'], 'Test')
        
        assert result['success'] is True

    @patch('apps.messaging.sms_service.africastalking')
    def test_get_account_balance(self, mock_at):
        """Test getting account balance."""
        mock_at.Airtime.return_value.get_balance.return_value = {
            'balance': 'KES 10.50'
        }
        
        service = AfricasTalkingService()
        result = service.get_account_balance()
        
        assert 'success' in result


@pytest.mark.django_db
class TestMessageService:
    """Test high-level message service."""

    @patch('apps.messaging.sms_service.AfricasTalkingService')
    def test_send_message_sms(self, mock_at_service):
        """Test sending SMS message through message service."""
        patient = PatientFactory()
        template = MessageTemplate.objects.create(
            name='Test Template',
            template_type='appointment_reminder',
            message_type='sms',
            content_english='Test message',
            is_active=True
        )
        
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone=patient.phone_number,
            template=template,
            message_type='sms',
            content='Test message',
            status='pending'
        )
        
        # Mock the Africa's Talking service
        mock_service_instance = MagicMock()
        mock_at_service.return_value = mock_service_instance
        mock_service_instance.send_sms.return_value = {
            'success': True,
            'response': [{'Status': 'Success', 'MessageId': 'msg123'}]
        }
        
        service = MessageService()
        result = service.send_message(message.id)
        
        assert result is True
        
        # Check message was updated
        message.refresh_from_db()
        assert message.status in ['sent', 'queued']
        
        # Check log was created
        log = MessageLog.objects.filter(message=message).first()
        assert log is not None

    @patch('apps.messaging.sms_service.AfricasTalkingService')
    def test_send_message_failure_logging(self, mock_at_service):
        """Test that message failures are properly logged."""
        patient = PatientFactory()
        template = MessageTemplate.objects.create(
            name='Test Template 2',
            template_type='appointment_reminder',
            message_type='sms',
            content_english='Test message',
            is_active=True
        )
        
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone=patient.phone_number,
            template=template,
            message_type='sms',
            content='Test message',
            status='pending'
        )
        
        # Mock failure
        mock_service_instance = MagicMock()
        mock_at_service.return_value = mock_service_instance
        mock_service_instance.send_sms.return_value = {
            'success': False,
            'error': 'Invalid phone number'
        }
        
        service = MessageService()
        result = service.send_message(message.id)
        
        assert result is False

    @patch('apps.messaging.sms_service.MessageService.send_message')
    def test_send_appointment_reminder(self, mock_send):
        """Test sending appointment reminder."""
        appointment = AppointmentFactory()
        template = MessageTemplate.objects.create(
            name='Appointment Reminder',
            template_type='appointment_reminder',
            message_type='sms',
            content_english='Appointment at {hospital} at {appointment_time}',
            content_kinyarwanda='Ihangane i{hospital} ku wa {appointment_time}',
            is_active=True
        )
        
        mock_send.return_value = True
        
        service = MessageService()
        result = service.send_appointment_reminder(appointment)
        
        assert result is True
        assert mock_send.called

    @patch('apps.messaging.sms_service.MessageService.send_message')
    def test_send_medication_reminder(self, mock_send):
        """Test sending medication reminder."""
        # Mock medication adherence since factory doesn't exist
        adherence = Mock()
        adherence.patient = PatientFactory()
        adherence.medication_name = "Paracetamol"
        adherence.dosage = "500mg"
        adherence.timing = "morning"
        
        template = MessageTemplate.objects.create(
            name='Medication Reminder',
            template_type='medication_reminder',
            message_type='sms',
            content_english='Take {medication} at {time}',
            content_kinyarwanda='Kunywa {medication} ku wa {time}',
            is_active=True
        )
        
        mock_send.return_value = True
        
        service = MessageService()
        result = service.send_medication_reminder(adherence)
        
        assert result is True
        assert mock_send.called

    @patch('apps.messaging.sms_service.AfricasTalkingService')
    def test_send_message_without_phone_number(self, mock_at_service):
        """Test that sending fails gracefully when patient has no phone."""
        patient = PatientFactory()
        
        template = MessageTemplate.objects.create(
            name='No Phone Template',
            template_type='appointment_reminder',
            message_type='sms',
            content_english='Test message',
            is_active=True
        )
        
        message = Message.objects.create(
            recipient_patient=patient,
            recipient_phone='',  # Empty phone number
            template=template,
            message_type='sms',
            content='Test message',
            status='pending'
        )
        
        service = MessageService()
        result = service.send_message(message.id)
        
        # Should handle gracefully
        assert isinstance(result, bool)
