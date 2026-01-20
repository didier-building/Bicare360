"""
Mock SMS service for demo mode without API credentials.

This service simulates SMS sending by logging messages to the database
without making actual API calls. Useful for:
- Development without API keys
- Demo environments
- Testing workflows without incurring costs
"""
import logging
from typing import Dict, List, Any
from django.conf import settings
from django.utils import timezone
from .models import Message, MessageLog

logger = logging.getLogger(__name__)


class MockSMSService:
    """
    Mock SMS service that simulates sending without real API calls.
    
    All "sent" messages are logged to the database with mock responses.
    This allows the complete workflow to function in demo mode.
    """

    def __init__(self):
        """Initialize mock SMS service."""
        self.demo_mode = getattr(settings, 'SMS_DEMO_MODE', True)
        logger.info("MockSMSService initialized (Demo Mode)")

    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Simulate sending SMS message.
        
        Args:
            phone: Recipient phone number (format: +250788123456)
            message: Message text to send
            
        Returns:
            dict: Mock response simulating Africa's Talking API
        """
        try:
            # Ensure phone number is in correct format
            if not phone.startswith('+'):
                phone = f"+{phone}"
            
            # Generate mock message ID
            mock_message_id = f"mock_sms_{timezone.now().timestamp()}"
            
            # Log the "sent" message
            logger.info(
                f"[MOCK SMS] To: {phone} | "
                f"Message: {message[:50]}{'...' if len(message) > 50 else ''} | "
                f"ID: {mock_message_id}"
            )
            
            return {
                'success': True,
                'message_id': mock_message_id,
                'phone': phone,
                'status': 'sent',
                'cost': '0.00',  # Mock cost
                'timestamp': timezone.now(),
                'mock': True  # Flag to indicate this is mock
            }
            
        except Exception as e:
            logger.error(f"Mock SMS error for {phone}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone': phone,
                'timestamp': timezone.now(),
                'mock': True
            }

    def send_bulk_sms(self, recipients: List[str], message: str) -> Dict[str, Any]:
        """
        Simulate sending SMS to multiple recipients.
        
        Args:
            recipients: List of phone numbers
            message: Message text to send to all recipients
            
        Returns:
            dict: Mock bulk response
        """
        try:
            # Format phone numbers
            formatted_recipients = [
                f"+{phone}" if not phone.startswith('+') else phone
                for phone in recipients
            ]
            
            # Generate mock message IDs
            mock_message_ids = [
                f"mock_sms_{timezone.now().timestamp()}_{i}"
                for i in range(len(recipients))
            ]
            
            logger.info(
                f"[MOCK BULK SMS] To: {len(recipients)} recipients | "
                f"Message: {message[:50]}{'...' if len(message) > 50 else ''}"
            )
            
            # Log individual "sends"
            for phone, msg_id in zip(formatted_recipients, mock_message_ids):
                logger.debug(f"[MOCK SMS] {msg_id} -> {phone}")
            
            return {
                'success': True,
                'message_ids': mock_message_ids,
                'count': len(recipients),
                'status': 'sent',
                'total_cost': '0.00',
                'timestamp': timezone.now(),
                'mock': True
            }
            
        except Exception as e:
            logger.error(f"Mock bulk SMS error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'count': len(recipients),
                'timestamp': timezone.now(),
                'mock': True
            }

    def send_whatsapp(
        self,
        phone: str,
        template_name: str,
        template_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Simulate sending WhatsApp template message.
        
        Args:
            phone: Recipient phone number
            template_name: WhatsApp template name
            template_data: Variables for template placeholders
            
        Returns:
            dict: Mock WhatsApp response
        """
        try:
            if not phone.startswith('+'):
                phone = f"+{phone}"
            
            mock_message_id = f"mock_whatsapp_{timezone.now().timestamp()}"
            
            logger.info(
                f"[MOCK WHATSAPP] To: {phone} | "
                f"Template: {template_name} | "
                f"Data: {template_data} | "
                f"ID: {mock_message_id}"
            )
            
            return {
                'success': True,
                'message_id': mock_message_id,
                'phone': phone,
                'template': template_name,
                'status': 'sent',
                'timestamp': timezone.now(),
                'mock': True
            }
            
        except Exception as e:
            logger.error(f"Mock WhatsApp error for {phone}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone': phone,
                'timestamp': timezone.now(),
                'mock': True
            }

    def check_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        Simulate checking message delivery status.
        
        Args:
            message_id: Message ID to check
            
        Returns:
            dict: Mock delivery status
        """
        logger.info(f"[MOCK STATUS CHECK] ID: {message_id}")
        
        # Always return success for mock messages
        return {
            'success': True,
            'message_id': message_id,
            'status': 'delivered',
            'delivered_at': timezone.now(),
            'mock': True
        }

    def get_balance(self) -> Dict[str, Any]:
        """
        Simulate getting account balance.
        
        Returns:
            dict: Mock balance information
        """
        logger.info("[MOCK BALANCE CHECK]")
        
        return {
            'success': True,
            'balance': 'UNLIMITED',  # Mock balance
            'currency': 'RWF',
            'mock': True
        }


class HybridSMSService:
    """
    Hybrid SMS service that uses real or mock based on configuration.
    
    Automatically switches between real Africa's Talking API and mock
    service based on settings and credential availability.
    """

    def __init__(self):
        """Initialize appropriate SMS service based on configuration."""
        from .sms_service import AfricasTalkingService
        
        self.demo_mode = getattr(settings, 'SMS_DEMO_MODE', False)
        
        # Check if API credentials are configured
        api_key = getattr(settings, 'AFRICASTALKING_API_KEY', '')
        has_credentials = bool(api_key and api_key != '')
        
        if self.demo_mode or not has_credentials:
            logger.info("Using MockSMSService (Demo Mode or No Credentials)")
            self.service = MockSMSService()
            self.is_mock = True
        else:
            logger.info("Using AfricasTalkingService (Real API)")
            self.service = AfricasTalkingService()
            self.is_mock = False

    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS via configured service."""
        return self.service.send_sms(phone, message)

    def send_bulk_sms(self, recipients: List[str], message: str) -> Dict[str, Any]:
        """Send bulk SMS via configured service."""
        return self.service.send_bulk_sms(recipients, message)

    def send_whatsapp(
        self,
        phone: str,
        template_name: str,
        template_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """Send WhatsApp message via configured service."""
        return self.service.send_whatsapp(phone, template_name, template_data)

    def check_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Check delivery status via configured service."""
        return self.service.check_delivery_status(message_id)

    def get_balance(self) -> Dict[str, Any]:
        """Get account balance via configured service."""
        return self.service.get_balance()

    def is_demo_mode(self) -> bool:
        """Check if running in demo mode."""
        return self.is_mock
