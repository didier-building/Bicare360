"""Tests for Africa's Talking service layer."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from apps.messaging.services import SMSService, WhatsAppService, send_sms, send_bulk_sms


@pytest.mark.django_db
class TestSMSService:
    """Test SMS service functionality."""
    
    @patch('apps.messaging.services.africastalking')
    def test_sms_service_initialization_success(self, mock_at):
        """Test successful initialization of SMS service."""
        mock_at.initialize.return_value = None
        
        service = SMSService()
        
        assert service.initialized is True
        mock_at.initialize.assert_called_once()
    
    @patch('apps.messaging.services.africastalking')
    def test_sms_service_initialization_failure(self, mock_at):
        """Test SMS service handles initialization failure."""
        mock_at.initialize.side_effect = Exception("API key invalid")
        
        service = SMSService()
        
        assert service.initialized is False
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_sms_success(self, mock_settings, mock_at):
        """Test successful SMS sending."""
        # Setup mocks
        mock_settings.AFRICASTALKING_USERNAME = "test_user"
        mock_settings.AFRICASTALKING_API_KEY = "test_key"
        mock_settings.AFRICASTALKING_SANDBOX = True
        mock_settings.AFRICASTALKING_FROM = "BiCare360"
        
        mock_sms = Mock()
        mock_at.SMS = mock_sms
        mock_sms.send.return_value = {
            'SMSMessageData': {
                'Recipients': [{
                    'number': '+250788123456',
                    'status': 'Success',
                    'messageId': 'AT-MSG-123',
                    'cost': 'RWF 10'
                }]
            }
        }
        
        service = SMSService()
        result = service.send_sms('+250788123456', 'Test message')
        
        assert result['success'] is True
        assert result['message_id'] == 'AT-MSG-123'
        assert result['status'] == 'Success'
        assert result['cost'] == 'RWF 10'
        mock_sms.send.assert_called_once()
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_sms_formats_phone_number(self, mock_settings, mock_at):
        """Test SMS service formats phone numbers correctly."""
        mock_settings.AFRICASTALKING_USERNAME = "test_user"
        mock_settings.AFRICASTALKING_API_KEY = "test_key"
        mock_settings.AFRICASTALKING_SANDBOX = True
        mock_settings.AFRICASTALKING_FROM = "BiCare360"
        
        mock_sms = Mock()
        mock_at.SMS = mock_sms
        mock_sms.send.return_value = {
            'SMSMessageData': {
                'Recipients': [{
                    'number': '+250788123456',
                    'status': 'Success',
                    'messageId': 'AT-MSG-123',
                    'cost': 'RWF 10'
                }]
            }
        }
        
        service = SMSService()
        result = service.send_sms('250788123456', 'Test message')  # Without +
        
        # Should add + prefix
        call_args = mock_sms.send.call_args
        assert call_args[1]['recipients'][0] == '+250788123456'
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_sms_failure(self, mock_settings, mock_at):
        """Test SMS sending handles API failure."""
        mock_settings.AFRICASTALKING_USERNAME = "test_user"
        mock_settings.AFRICASTALKING_API_KEY = "test_key"
        mock_settings.AFRICASTALKING_SANDBOX = True
        
        mock_sms = Mock()
        mock_at.SMS = mock_sms
        mock_sms.send.return_value = {
            'SMSMessageData': {
                'Recipients': [{
                    'number': '+250788123456',
                    'status': 'Failed',
                    'messageId': None,
                }]
            }
        }
        
        service = SMSService()
        result = service.send_sms('+250788123456', 'Test message')
        
        assert result['success'] is False
        assert result['status'] == 'Failed'
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_sms_exception_handling(self, mock_settings, mock_at):
        """Test SMS service handles exceptions gracefully."""
        mock_settings.AFRICASTALKING_USERNAME = "test_user"
        mock_settings.AFRICASTALKING_API_KEY = "test_key"
        mock_settings.AFRICASTALKING_SANDBOX = True
        
        mock_sms = Mock()
        mock_at.SMS = mock_sms
        mock_sms.send.side_effect = Exception("Network error")
        
        service = SMSService()
        result = service.send_sms('+250788123456', 'Test message')
        
        assert result['success'] is False
        assert 'Network error' in result['error']
        assert result['status'] == 'error'
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_sms_not_configured(self, mock_settings, mock_at):
        """Test SMS sending when service not configured."""
        mock_settings.AFRICASTALKING_USERNAME = ""
        mock_settings.AFRICASTALKING_API_KEY = ""
        mock_settings.AFRICASTALKING_SANDBOX = False
        
        service = SMSService()
        result = service.send_sms('+250788123456', 'Test message')
        
        assert result['success'] is False
        assert 'not configured' in result['error']
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_bulk_sms_success(self, mock_settings, mock_at):
        """Test successful bulk SMS sending."""
        mock_settings.AFRICASTALKING_USERNAME = "test_user"
        mock_settings.AFRICASTALKING_API_KEY = "test_key"
        mock_settings.AFRICASTALKING_SANDBOX = True
        mock_settings.AFRICASTALKING_FROM = "BiCare360"
        
        mock_sms = Mock()
        mock_at.SMS = mock_sms
        mock_sms.send.return_value = {
            'SMSMessageData': {
                'Recipients': [
                    {
                        'number': '+250788123456',
                        'status': 'Success',
                        'messageId': 'AT-MSG-123',
                        'cost': 'RWF 10'
                    },
                    {
                        'number': '+250788654321',
                        'status': 'Success',
                        'messageId': 'AT-MSG-124',
                        'cost': 'RWF 10'
                    }
                ]
            }
        }
        
        service = SMSService()
        recipients = ['+250788123456', '+250788654321']
        result = service.send_bulk_sms(recipients, 'Bulk message')
        
        assert result['success'] is True
        assert result['total'] == 2
        assert result['successful'] == 2
        assert result['failed'] == 0
        assert len(result['results']) == 2
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_bulk_sms_partial_failure(self, mock_settings, mock_at):
        """Test bulk SMS with some failures."""
        mock_settings.AFRICASTALKING_USERNAME = "test_user"
        mock_settings.AFRICASTALKING_API_KEY = "test_key"
        mock_settings.AFRICASTALKING_SANDBOX = True
        mock_settings.AFRICASTALKING_FROM = "BiCare360"
        
        mock_sms = Mock()
        mock_at.SMS = mock_sms
        mock_sms.send.return_value = {
            'SMSMessageData': {
                'Recipients': [
                    {
                        'number': '+250788123456',
                        'status': 'Success',
                        'messageId': 'AT-MSG-123',
                        'cost': 'RWF 10'
                    },
                    {
                        'number': '+250788654321',
                        'status': 'Failed',
                        'messageId': None,
                    }
                ]
            }
        }
        
        service = SMSService()
        recipients = ['+250788123456', '+250788654321']
        result = service.send_bulk_sms(recipients, 'Bulk message')
        
        assert result['success'] is True
        assert result['total'] == 2
        assert result['successful'] == 1
        assert result['failed'] == 1


@pytest.mark.django_db
class TestWhatsAppService:
    """Test WhatsApp service functionality."""
    
    @patch('apps.messaging.services.africastalking')
    def test_whatsapp_service_initialization(self, mock_at):
        """Test WhatsApp service initialization."""
        mock_at.initialize.return_value = None
        
        service = WhatsAppService()
        
        assert service.initialized is True
    
    @patch('apps.messaging.services.africastalking')
    @patch('apps.messaging.services.settings')
    def test_send_whatsapp_not_fully_implemented(self, mock_settings, mock_at):
        """Test WhatsApp sending returns pending status."""
        mock_settings.AFRICASTALKING_USERNAME = "test_user"
        mock_settings.AFRICASTALKING_API_KEY = "test_key"
        mock_settings.AFRICASTALKING_SANDBOX = True
        
        service = WhatsAppService()
        result = service.send_whatsapp('+250788123456', 'Test WhatsApp message')
        
        # WhatsApp requires template approval, so should return pending
        assert result['success'] is False
        assert 'template approval' in result['error'].lower()
        assert result['status'] == 'pending_setup'
    
    @patch('apps.messaging.services.africastalking')
    def test_get_template_list(self, mock_at):
        """Test getting WhatsApp template list."""
        service = WhatsAppService()
        templates = service.get_template_list()
        
        # Currently returns empty list as placeholder
        assert isinstance(templates, list)


@pytest.mark.django_db
class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('apps.messaging.mock_sms_service.HybridSMSService')
    def test_send_sms_function(self, mock_service_class):
        """Test send_sms convenience function."""
        mock_service = Mock()
        mock_service.send_sms.return_value = {'success': True}
        mock_service_class.return_value = mock_service
        
        result = send_sms('+250788123456', 'Test')
        
        assert result['success'] is True
        mock_service.send_sms.assert_called_once_with('+250788123456', 'Test')
    
    @patch('apps.messaging.mock_sms_service.HybridSMSService')
    def test_send_bulk_sms_function(self, mock_service_class):
        """Test send_bulk_sms convenience function."""
        mock_service = Mock()
        mock_service.send_bulk_sms.return_value = {'success': True, 'total': 2}
        mock_service_class.return_value = mock_service
        
        recipients = ['+250788123456', '+250788654321']
        result = send_bulk_sms(recipients, 'Bulk test')
        
        assert result['success'] is True
        assert result['total'] == 2
        mock_service.send_bulk_sms.assert_called_once_with(recipients, 'Bulk test')
