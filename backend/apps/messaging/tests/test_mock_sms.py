"""
Tests for mock SMS service and hybrid SMS functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from apps.messaging.mock_sms_service import MockSMSService, HybridSMSService


class TestMockSMSService:
    """Test suite for MockSMSService."""
    
    @pytest.fixture
    def mock_sms_service(self):
        """Create MockSMSService instance."""
        return MockSMSService()
    
    def test_send_sms_success(self, mock_sms_service):
        """Test successful SMS sending."""
        result = mock_sms_service.send_sms(
            phone="+250788123456",
            message="Test message"
        )
        
        assert result['success'] is True
        assert result['phone'] == "+250788123456"
        assert result['status'] == 'sent'
        assert result['mock'] is True
        assert 'message_id' in result
        assert result['message_id'].startswith('mock_sms_')
    
    def test_send_sms_formats_phone_number(self, mock_sms_service):
        """Test phone number formatting."""
        result = mock_sms_service.send_sms(
            phone="250788123456",  # Without +
            message="Test"
        )
        
        assert result['success'] is True
        assert result['phone'] == "+250788123456"
    
    def test_send_bulk_sms_success(self, mock_sms_service):
        """Test successful bulk SMS sending."""
        recipients = ["+250788123456", "+250788654321", "250788111222"]
        result = mock_sms_service.send_bulk_sms(
            recipients=recipients,
            message="Bulk test message"
        )
        
        assert result['success'] is True
        assert result['count'] == 3
        assert result['status'] == 'sent'
        assert result['mock'] is True
        assert len(result['message_ids']) == 3
    
    def test_send_whatsapp_success(self, mock_sms_service):
        """Test successful WhatsApp message simulation."""
        result = mock_sms_service.send_whatsapp(
            phone="+250788123456",
            template_name="appointment_reminder",
            template_data={'patient_name': 'John Doe', 'date': '2026-01-25'}
        )
        
        assert result['success'] is True
        assert result['phone'] == "+250788123456"
        assert result['template'] == "appointment_reminder"
        assert result['status'] == 'sent'
        assert result['mock'] is True
    
    def test_check_delivery_status(self, mock_sms_service):
        """Test delivery status check."""
        result = mock_sms_service.check_delivery_status("mock_sms_12345")
        
        assert result['success'] is True
        assert result['message_id'] == "mock_sms_12345"
        assert result['status'] == 'delivered'
        assert result['mock'] is True
    
    def test_get_balance(self, mock_sms_service):
        """Test balance check."""
        result = mock_sms_service.get_balance()
        
        assert result['success'] is True
        assert result['balance'] == 'UNLIMITED'
        assert result['mock'] is True


class TestHybridSMSService:
    """Test suite for HybridSMSService."""
    
    @pytest.fixture
    def hybrid_service_mock_mode(self, settings):
        """Create HybridSMSService in mock mode."""
        settings.SMS_DEMO_MODE = True
        settings.AFRICASTALKING_API_KEY = ""
        return HybridSMSService()
    
    @pytest.fixture
    def hybrid_service_real_mode(self, settings):
        """Create HybridSMSService in real mode (with credentials)."""
        settings.SMS_DEMO_MODE = False
        settings.AFRICASTALKING_API_KEY = "test-api-key-12345"
        settings.AFRICASTALKING_USERNAME = "test-username"
        with patch('apps.messaging.mock_sms_service.AfricasTalkingService'):
            return HybridSMSService()
    
    def test_uses_mock_when_demo_mode(self, hybrid_service_mock_mode):
        """Test that mock service is used when demo mode is enabled."""
        assert hybrid_service_mock_mode.is_mock is True
        assert isinstance(hybrid_service_mock_mode.service, MockSMSService)
    
    def test_uses_mock_when_no_credentials(self, settings):
        """Test that mock service is used when credentials are missing."""
        settings.SMS_DEMO_MODE = False
        settings.AFRICASTALKING_API_KEY = ""
        service = HybridSMSService()
        
        assert service.is_mock is True
        assert isinstance(service.service, MockSMSService)
    
    def test_send_sms_in_mock_mode(self, hybrid_service_mock_mode):
        """Test SMS sending in mock mode."""
        result = hybrid_service_mock_mode.send_sms(
            phone="+250788123456",
            message="Test"
        )
        
        assert result['success'] is True
        assert result['mock'] is True
    
    def test_send_bulk_sms_in_mock_mode(self, hybrid_service_mock_mode):
        """Test bulk SMS in mock mode."""
        result = hybrid_service_mock_mode.send_bulk_sms(
            recipients=["+250788123456", "+250788654321"],
            message="Bulk test"
        )
        
        assert result['success'] is True
        assert result['mock'] is True
        assert result['count'] == 2
    
    def test_is_demo_mode_returns_true_in_mock(self, hybrid_service_mock_mode):
        """Test is_demo_mode returns correct value."""
        assert hybrid_service_mock_mode.is_demo_mode() is True
    
    def test_send_whatsapp_in_mock_mode(self, hybrid_service_mock_mode):
        """Test WhatsApp sending in mock mode."""
        result = hybrid_service_mock_mode.send_whatsapp(
            phone="+250788123456",
            template_name="test_template",
            template_data={}
        )
        
        assert result['success'] is True
        assert result['mock'] is True


@pytest.mark.django_db
class TestServiceIntegration:
    """Integration tests for messaging services."""
    
    def test_convenience_function_send_sms(self, settings):
        """Test send_sms convenience function."""
        from apps.messaging.services import send_sms
        
        settings.SMS_DEMO_MODE = True
        result = send_sms("+250788123456", "Test message")
        
        assert result['success'] is True
        assert result['mock'] is True
    
    def test_convenience_function_send_bulk_sms(self, settings):
        """Test send_bulk_sms convenience function."""
        from apps.messaging.services import send_bulk_sms
        
        settings.SMS_DEMO_MODE = True
        result = send_bulk_sms(
            ["+250788123456", "+250788654321"],
            "Bulk message"
        )
        
        assert result['success'] is True
        assert result['mock'] is True
    
    def test_convenience_function_is_demo_mode(self, settings):
        """Test is_demo_mode convenience function."""
        from apps.messaging.services import is_demo_mode
        
        settings.SMS_DEMO_MODE = True
        assert is_demo_mode() is True
        
        settings.SMS_DEMO_MODE = False
        settings.AFRICASTALKING_API_KEY = ""
        assert is_demo_mode() is True  # Still mock due to missing credentials
