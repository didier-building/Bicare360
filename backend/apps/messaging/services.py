"""
Unified message service layer for SMS, WhatsApp, and Email messaging.

This module provides wrapper classes for interacting with messaging services,
including Africa's Talking API and mock services for demo mode.
"""
import logging
import africastalking
from django.conf import settings
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class AfricasTalkingService:
    """Base service for Africa's Talking API integration."""
    
    def __init__(self):
        """Initialize Africa's Talking SDK."""
        try:
            africastalking.initialize(
                username=settings.AFRICASTALKING_USERNAME,
                api_key=settings.AFRICASTALKING_API_KEY
            )
            self.initialized = True
            logger.info(f"Africa's Talking initialized (sandbox: {settings.AFRICASTALKING_SANDBOX})")
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking: {e}")
            self.initialized = False
    
    def is_configured(self) -> bool:
        """Check if Africa's Talking is properly configured."""
        return (
            self.initialized and
            settings.AFRICASTALKING_USERNAME and
            settings.AFRICASTALKING_API_KEY and
            settings.AFRICASTALKING_USERNAME != "sandbox" or settings.AFRICASTALKING_SANDBOX
        )


class SMSService(AfricasTalkingService):
    """Service for sending SMS messages via Africa's Talking."""
    
    def __init__(self):
        super().__init__()
        if self.initialized:
            self.sms = africastalking.SMS
    
    def send_sms(
        self,
        recipient: str,
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict:
        """
        Send SMS message to a single recipient.
        
        Args:
            recipient: Phone number in international format (e.g., +250788123456)
            message: Message content
            sender_id: Optional sender ID (defaults to settings value)
            
        Returns:
            dict: Response from Africa's Talking API
            {
                'success': bool,
                'message_id': str,
                'status': str,
                'cost': str,
                'error': str (optional)
            }
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Africa\'s Talking is not configured',
                'message_id': None,
                'status': 'not_configured'
            }
        
        try:
            # Ensure phone number is in correct format
            if not recipient.startswith('+'):
                recipient = f'+{recipient}'
            
            # Use default sender ID from settings if not provided
            if not sender_id:
                sender_id = settings.AFRICASTALKING_FROM
            
            # Send SMS
            response = self.sms.send(
                message=message,
                recipients=[recipient],
                sender_id=sender_id
            )
            
            logger.info(f"SMS API response: {response}")
            
            # Parse response
            if response['SMSMessageData']['Recipients']:
                recipient_data = response['SMSMessageData']['Recipients'][0]
                
                return {
                    'success': recipient_data['status'] in ['Success', 'Sent'],
                    'message_id': recipient_data.get('messageId'),
                    'status': recipient_data['status'],
                    'cost': recipient_data.get('cost', '0'),
                    'phone': recipient_data.get('number')
                }
            else:
                return {
                    'success': False,
                    'error': 'No recipient data in response',
                    'message_id': None,
                    'status': 'failed'
                }
                
        except Exception as e:
            logger.error(f"Error sending SMS to {recipient}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None,
                'status': 'error'
            }
    
    def send_bulk_sms(
        self,
        recipients: List[str],
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict:
        """
        Send SMS to multiple recipients.
        
        Args:
            recipients: List of phone numbers in international format
            message: Message content
            sender_id: Optional sender ID
            
        Returns:
            dict: Response with results for each recipient
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Africa\'s Talking is not configured',
                'results': []
            }
        
        try:
            # Format phone numbers
            formatted_recipients = [
                f'+{r}' if not r.startswith('+') else r
                for r in recipients
            ]
            
            if not sender_id:
                sender_id = settings.AFRICASTALKING_FROM
            
            # Send bulk SMS
            response = self.sms.send(
                message=message,
                recipients=formatted_recipients,
                sender_id=sender_id
            )
            
            # Parse results
            results = []
            if response['SMSMessageData']['Recipients']:
                for recipient_data in response['SMSMessageData']['Recipients']:
                    results.append({
                        'phone': recipient_data.get('number'),
                        'success': recipient_data['status'] in ['Success', 'Sent'],
                        'message_id': recipient_data.get('messageId'),
                        'status': recipient_data['status'],
                        'cost': recipient_data.get('cost', '0')
                    })
            
            successful = sum(1 for r in results if r['success'])
            
            return {
                'success': True,
                'total': len(recipients),
                'successful': successful,
                'failed': len(recipients) - successful,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error sending bulk SMS: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }


class WhatsAppService(AfricasTalkingService):
    """Service for sending WhatsApp messages via Africa's Talking."""
    
    def __init__(self):
        super().__init__()
        if self.initialized:
            self.whatsapp = africastalking.Airtime  # Note: WhatsApp uses Airtime service
    
    def send_whatsapp(
        self,
        recipient: str,
        message: str,
        template_name: Optional[str] = None
    ) -> Dict:
        """
        Send WhatsApp message to a single recipient.
        
        Note: Africa's Talking WhatsApp requires pre-approved templates.
        
        Args:
            recipient: Phone number in international format
            message: Message content (must match approved template)
            template_name: Optional template name
            
        Returns:
            dict: Response from Africa's Talking API
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Africa\'s Talking is not configured',
                'message_id': None,
                'status': 'not_configured'
            }
        
        try:
            # Format phone number
            if not recipient.startswith('+'):
                recipient = f'+{recipient}'
            
            # Note: Actual WhatsApp API call would go here
            # For now, this is a placeholder as Africa's Talking WhatsApp
            # requires additional setup and template approval
            
            logger.warning(
                "WhatsApp sending is not fully implemented. "
                "Requires template approval from Africa's Talking."
            )
            
            return {
                'success': False,
                'error': 'WhatsApp not fully configured (requires template approval)',
                'message_id': None,
                'status': 'pending_setup'
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {recipient}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None,
                'status': 'error'
            }
    
    def get_template_list(self) -> List[Dict]:
        """
        Get list of approved WhatsApp templates.
        
        Returns:
            list: List of approved templates
        """
        # Placeholder - would fetch from Africa's Talking API
        logger.warning("WhatsApp template fetching not implemented")
        return []


# Convenience functions for easy access
def send_sms(recipient: str, message: str, sender_id: Optional[str] = None) -> Dict:
    """
    Send SMS message using appropriate service (real or mock).
    
    Automatically selects between Africa's Talking and Mock service
    based on SMS_DEMO_MODE setting and credential availability.
    """
    from .mock_sms_service import HybridSMSService
    service = HybridSMSService()
    return service.send_sms(recipient, message)


def send_bulk_sms(recipients: List[str], message: str, sender_id: Optional[str] = None) -> Dict:
    """Send bulk SMS messages using appropriate service."""
    from .mock_sms_service import HybridSMSService
    service = HybridSMSService()
    return service.send_bulk_sms(recipients, message)


def send_whatsapp(recipient: str, message: str, template_name: Optional[str] = None) -> Dict:
    """Send WhatsApp message using appropriate service."""
    from .mock_sms_service import HybridSMSService
    service = HybridSMSService()
    return service.send_whatsapp(recipient, template_name, {})


def is_demo_mode() -> bool:
    """Check if messaging is running in demo mode."""
    from .mock_sms_service import HybridSMSService
    service = HybridSMSService()
    return service.is_demo_mode()
