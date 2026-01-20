"""
SMS and WhatsApp service integration with Africa's Talking.

Handles sending SMS and WhatsApp messages through Africa's Talking API.
"""
import africastalking
import logging
from typing import Dict, List, Any
from django.conf import settings
from django.utils import timezone
from .models import Message, MessageLog, MessageTemplate
from .email_service import EmailService

logger = logging.getLogger(__name__)


class AfricasTalkingService:
    """Handle Africa's Talking API integration for SMS and WhatsApp."""

    def __init__(self):
        """Initialize Africa's Talking client."""
        africastalking.initialize(
            username=settings.AFRICASTALKING_USERNAME,
            api_key=settings.AFRICASTALKING_API_KEY
        )
        self.sms = africastalking.SMS
        self.whatsapp = africastalking.Whatsapp  # Note: lowercase 'app'

    def send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send SMS message via Africa's Talking.
        
        Args:
            phone: Recipient phone number (format: +250788123456)
            message: Message text to send
            
        Returns:
            dict: Response from Africa's Talking API
        """
        try:
            # Ensure phone number is in correct format
            if not phone.startswith('+'):
                phone = f"+{phone}"
            
            response = self.sms.send(message, [phone])
            logger.info(f"SMS sent to {phone}: {response}")
            return {
                'success': True,
                'response': response,
                'phone': phone,
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone': phone,
                'timestamp': timezone.now()
            }

    def send_bulk_sms(self, recipients: List[str], message: str) -> Dict[str, Any]:
        """
        Send SMS to multiple recipients.
        
        Args:
            recipients: List of phone numbers
            message: Message text to send to all recipients
            
        Returns:
            dict: Response from Africa's Talking API
        """
        try:
            # Format phone numbers
            formatted_recipients = [
                f"+{phone}" if not phone.startswith('+') else phone
                for phone in recipients
            ]
            
            response = self.sms.send(message, formatted_recipients)
            logger.info(f"Bulk SMS sent to {len(recipients)} recipients: {response}")
            return {
                'success': True,
                'response': response,
                'count': len(recipients),
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Failed to send bulk SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'count': len(recipients),
                'timestamp': timezone.now()
            }

    def send_whatsapp(self, phone: str, template_name: str, 
                     template_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Send WhatsApp template message via Africa's Talking.
        
        Args:
            phone: Recipient phone number
            template_name: Name of the WhatsApp template
            template_data: Dictionary of template variables
            
        Returns:
            dict: Response from Africa's Talking API
        """
        try:
            # Ensure phone number is in correct format
            if not phone.startswith('+'):
                phone = f"+{phone}"
            
            response = self.whatsapp.send_template(
                phone=phone,
                template_name=template_name,
                template_data=template_data
            )
            logger.info(f"WhatsApp sent to {phone}: {response}")
            return {
                'success': True,
                'response': response,
                'phone': phone,
                'template': template_name,
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {phone}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone': phone,
                'template': template_name,
                'timestamp': timezone.now()
            }

    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance from Africa's Talking.
        
        Returns:
            dict: Account balance information
        """
        try:
            response = self.sms.get_balance()
            logger.info(f"Account balance: {response}")
            return {
                'success': True,
                'balance': response,
                'timestamp': timezone.now()
            }
        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': timezone.now()
            }


class MessageService:
    """High-level service for sending messages through various channels."""

    def __init__(self):
        """Initialize message service."""
        self.at_service = AfricasTalkingService()
        self.email_service = EmailService()

    def send_message(self, message_id: int) -> bool:
        """
        Send a message via the appropriate channel (SMS, WhatsApp, or Email).
        
        Args:
            message_id: ID of the message to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            message = Message.objects.get(id=message_id)
            
            if message.message_type == 'sms':
                return self._send_sms_message(message)
            elif message.message_type == 'whatsapp':
                return self._send_whatsapp_message(message)
            elif message.message_type == 'email':
                return self._send_email_message(message)
            else:
                logger.error(f"Unknown message type: {message.message_type}")
                return False
                
        except Message.DoesNotExist:
            logger.error(f"Message with id {message_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error sending message {message_id}: {str(e)}")
            return False

    def _send_sms_message(self, message: Message) -> bool:
        """Send SMS message."""
        try:
            # Get phone number
            phone = message.recipient_patient.phone_number
            if not phone:
                logger.error(f"No phone number for patient {message.recipient_patient.id}")
                return False
            
            # Send SMS
            result = self.at_service.send_sms(phone, message.content)
            
            if result['success']:
                # Log success
                MessageLog.objects.create(
                    message=message,
                    status='sent',
                    provider_response=str(result['response'])
                )
                message.status = 'sent'
                message.sent_at = timezone.now()
                message.save()
                logger.info(f"SMS sent successfully to {phone}")
                return True
            else:
                # Log failure
                MessageLog.objects.create(
                    message=message,
                    status='failed',
                    error_message=result['error']
                )
                message.status = 'failed'
                message.save()
                logger.error(f"Failed to send SMS: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error in _send_sms_message: {str(e)}")
            MessageLog.objects.create(
                message=message,
                status='failed',
                error_message=str(e)
            )
            message.status = 'failed'
            message.save()
            return False

    def _send_whatsapp_message(self, message: Message) -> bool:
        """Send WhatsApp template message."""
        try:
            # Get phone number
            phone = message.recipient_patient.phone_number
            if not phone:
                logger.error(f"No phone number for patient {message.recipient_patient.id}")
                return False
            
            # Get template information from message
            template_name = getattr(message, 'template_name', None)
            template_data = getattr(message, 'template_variables', {})
            
            if not template_name:
                logger.error(f"No template name for message {message.id}")
                return False
            
            # Send WhatsApp
            result = self.at_service.send_whatsapp(phone, template_name, template_data)
            
            if result['success']:
                # Log success
                MessageLog.objects.create(
                    message=message,
                    status='sent',
                    provider_response=str(result['response'])
                )
                message.status = 'sent'
                message.sent_at = timezone.now()
                message.save()
                logger.info(f"WhatsApp sent successfully to {phone}")
                return True
            else:
                # Log failure
                MessageLog.objects.create(
                    message=message,
                    status='failed',
                    error_message=result['error']
                )
                message.status = 'failed'
                message.save()
                logger.error(f"Failed to send WhatsApp: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error in _send_whatsapp_message: {str(e)}")
            MessageLog.objects.create(
                message=message,
                status='failed',
                error_message=str(e)
            )
            message.status = 'failed'
            message.save()
            return False

    def _send_email_message(self, message: Message) -> bool:
        """Send email message."""
        try:
            # Get patient email
            patient = message.recipient_patient
            email = getattr(patient, 'email', None)
            
            if not email:
                logger.error(f"No email for patient {patient.id}")
                MessageLog.objects.create(
                    message=message,
                    status='failed',
                    error_message='Patient has no email address'
                )
                message.status = 'failed'
                message.save()
                return False
            
            # Send email
            result = self.email_service.send_email(
                to_email=email,
                subject=f"BiCare360 Notification",
                message=message.content,
                html_message=None  # Use plain content for now
            )
            
            if result['success']:
                # Log success
                MessageLog.objects.create(
                    message=message,
                    status='sent',
                    provider_response=f"Email sent to {email}"
                )
                message.status = 'sent'
                message.sent_at = timezone.now()
                message.save()
                logger.info(f"Email sent successfully to {email}")
                return True
            else:
                # Log failure
                MessageLog.objects.create(
                    message=message,
                    status='failed',
                    error_message=result['error']
                )
                message.status = 'failed'
                message.save()
                logger.error(f"Failed to send email: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Error in _send_email_message: {str(e)}")
            MessageLog.objects.create(
                message=message,
                status='failed',
                error_message=str(e)
            )
            message.status = 'failed'
            message.save()
            return False

    def send_appointment_reminder(self, appointment) -> bool:
        """
        Send appointment reminder to patient.
        
        Args:
            appointment: Appointment object
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Get or create reminder template
            template = MessageTemplate.objects.filter(
                template_type='appointment_reminder',
                is_active=True
            ).first()
            
            if not template:
                logger.error("No active appointment_reminder template found")
                return False
            
            # Render template content
            content = template.content_kinyarwanda or template.content_english
            try:
                content = content.format(
                    patient_name=appointment.patient.first_name,
                    hospital=appointment.hospital.name,
                    hospital_name=appointment.hospital.name,  # Support both formats
                    appointment_time=appointment.appointment_datetime.strftime('%H:%M'),
                    appointment_date=appointment.appointment_datetime.strftime('%d-%m-%Y')
                )
            except KeyError as e:
                logger.error(f"Template formatting error: missing key {e}")
                return False
            
            # Create message
            message = Message.objects.create(
                recipient_patient=appointment.patient,
                recipient_phone=appointment.patient.phone_number,
                template=template,
                appointment=appointment,
                message_type='sms',
                content=content,
                status='pending'
            )
            
            # Send immediately
            return self.send_message(message.id)
            
        except Exception as e:
            logger.error(f"Error sending appointment reminder: {str(e)}")
            return False

    def send_medication_reminder(self, adherence) -> bool:
        """
        Send medication reminder to patient.
        
        Args:
            adherence: MedicationAdherence object
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Get or create reminder template
            template = MessageTemplate.objects.filter(
                template_type='medication_reminder',
                is_active=True
            ).first()
            
            if not template:
                logger.error("No active medication_reminder template found")
                return False
            
            # Render template content
            content = template.content_kinyarwanda or template.content_english
            content = content.format(
                patient_name=adherence.patient.first_name,
                medication=adherence.prescription.medication.name,
                time=adherence.scheduled_time.strftime('%H:%M') if adherence.scheduled_time else 'now'
            )
            
            # Create message
            message = Message.objects.create(
                recipient_patient=adherence.patient,
                recipient_phone=adherence.patient.phone_number,
                template=template,
                message_type='sms',
                content=content,
                status='pending'
            )
            
            # Send immediately
            return self.send_message(message.id)
            
        except Exception as e:
            logger.error(f"Error sending medication reminder: {str(e)}")
            return False
