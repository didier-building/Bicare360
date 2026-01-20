"""
Email service for sending notifications.
"""
import logging
from typing import Dict, List, Optional
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        """Initialize email service."""
        self.from_email = settings.DEFAULT_FROM_EMAIL

    def send_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None
    ) -> Dict:
        """
        Send a single email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            message: Plain text message
            html_message: Optional HTML version of the message
            
        Returns:
            Dict with success status and details
        """
        try:
            if html_message:
                # Send both plain text and HTML versions
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=self.from_email,
                    to=[to_email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                # Send plain text only
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=self.from_email,
                    recipient_list=[to_email],
                    fail_silently=False,
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                'success': True,
                'recipient': to_email,
                'subject': subject,
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recipient': to_email,
                'timestamp': timezone.now()
            }

    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        message: str,
        html_message: Optional[str] = None
    ) -> Dict:
        """
        Send email to multiple recipients.
        
        Args:
            recipients: List of email addresses
            subject: Email subject line
            message: Plain text message
            html_message: Optional HTML version
            
        Returns:
            Dict with success status and results per recipient
        """
        results = []
        success_count = 0
        failure_count = 0

        for recipient in recipients:
            result = self.send_email(recipient, subject, message, html_message)
            results.append(result)
            if result['success']:
                success_count += 1
            else:
                failure_count += 1

        logger.info(f"Bulk email: {success_count} sent, {failure_count} failed")
        
        return {
            'success': failure_count == 0,
            'total': len(recipients),
            'sent': success_count,
            'failed': failure_count,
            'results': results,
            'timestamp': timezone.now()
        }

    def send_appointment_reminder_email(
        self,
        patient_email: str,
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        hospital_name: str,
        provider_name: str,
        appointment_type: str
    ) -> Dict:
        """
        Send appointment reminder email.
        
        Args:
            patient_email: Patient's email address
            patient_name: Patient's full name
            appointment_date: Date of appointment
            appointment_time: Time of appointment
            hospital_name: Hospital name
            provider_name: Provider's name
            appointment_type: Type of appointment
            
        Returns:
            Dict with success status
        """
        subject = f"Appointment Reminder - {appointment_date}"
        
        # Plain text message
        message = f"""
Dear {patient_name},

This is a reminder about your upcoming appointment:

Date: {appointment_date}
Time: {appointment_time}
Location: {hospital_name}
Provider: {provider_name}
Type: {appointment_type}

Please arrive 15 minutes early for registration.

If you need to reschedule, please contact us as soon as possible.

Best regards,
BiCare360 Team
        """.strip()
        
        # HTML message (optional, can be enhanced with templates)
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Appointment Reminder</h2>
                <p>Dear {patient_name},</p>
                <p>This is a reminder about your upcoming appointment:</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Date:</strong> {appointment_date}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {appointment_time}</p>
                    <p style="margin: 5px 0;"><strong>Location:</strong> {hospital_name}</p>
                    <p style="margin: 5px 0;"><strong>Provider:</strong> {provider_name}</p>
                    <p style="margin: 5px 0;"><strong>Type:</strong> {appointment_type}</p>
                </div>
                
                <p>Please arrive 15 minutes early for registration.</p>
                <p>If you need to reschedule, please contact us as soon as possible.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>BiCare360 Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(patient_email, subject, message, html_message)

    def send_medication_reminder_email(
        self,
        patient_email: str,
        patient_name: str,
        medication_name: str,
        dosage: str,
        timing: str,
        instructions: str
    ) -> Dict:
        """
        Send medication reminder email.
        
        Args:
            patient_email: Patient's email address
            patient_name: Patient's full name
            medication_name: Name of medication
            dosage: Dosage information
            timing: When to take medication
            instructions: Additional instructions
            
        Returns:
            Dict with success status
        """
        subject = f"Medication Reminder - {medication_name}"
        
        # Plain text message
        message = f"""
Dear {patient_name},

This is a reminder to take your medication:

Medication: {medication_name}
Dosage: {dosage}
Timing: {timing}

Instructions: {instructions}

Please take your medication as prescribed. If you have any side effects or concerns, contact your healthcare provider.

Best regards,
BiCare360 Team
        """.strip()
        
        # HTML message
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">💊 Medication Reminder</h2>
                <p>Dear {patient_name},</p>
                <p>This is a reminder to take your medication:</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Medication:</strong> {medication_name}</p>
                    <p style="margin: 5px 0;"><strong>Dosage:</strong> {dosage}</p>
                    <p style="margin: 5px 0;"><strong>Timing:</strong> {timing}</p>
                </div>
                
                <div style="background-color: #fef3c7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Instructions:</strong></p>
                    <p style="margin: 5px 0;">{instructions}</p>
                </div>
                
                <p>Please take your medication as prescribed. If you have any side effects or concerns, contact your healthcare provider.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>BiCare360 Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(patient_email, subject, message, html_message)

    def send_discharge_summary_email(
        self,
        patient_email: str,
        patient_name: str,
        hospital_name: str,
        discharge_date: str,
        diagnosis: str,
        follow_up_instructions: str
    ) -> Dict:
        """
        Send discharge summary email.
        
        Args:
            patient_email: Patient's email address
            patient_name: Patient's full name
            hospital_name: Hospital name
            discharge_date: Date of discharge
            diagnosis: Diagnosis summary
            follow_up_instructions: Follow-up instructions
            
        Returns:
            Dict with success status
        """
        subject = f"Discharge Summary - {hospital_name}"
        
        message = f"""
Dear {patient_name},

You have been discharged from {hospital_name} on {discharge_date}.

Diagnosis: {diagnosis}

Follow-up Instructions:
{follow_up_instructions}

Please follow all instructions carefully and attend your scheduled follow-up appointments.

If you experience any concerning symptoms, please contact your healthcare provider immediately.

Best regards,
BiCare360 Team
        """.strip()
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">🏥 Discharge Summary</h2>
                <p>Dear {patient_name},</p>
                <p>You have been discharged from <strong>{hospital_name}</strong> on {discharge_date}.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Diagnosis:</strong></p>
                    <p style="margin: 5px 0;">{diagnosis}</p>
                </div>
                
                <div style="background-color: #dbeafe; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Follow-up Instructions:</strong></p>
                    <p style="margin: 5px 0; white-space: pre-wrap;">{follow_up_instructions}</p>
                </div>
                
                <p>Please follow all instructions carefully and attend your scheduled follow-up appointments.</p>
                
                <p style="background-color: #fee2e2; padding: 10px; border-radius: 5px;">
                    ⚠️ If you experience any concerning symptoms, please contact your healthcare provider immediately.
                </p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>BiCare360 Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(patient_email, subject, message, html_message)
