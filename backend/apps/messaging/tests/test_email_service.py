"""
Tests for email notification service and Celery tasks.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from apps.messaging.email_service import EmailService
from apps.messaging.tasks import (
    send_email_notification_task,
    send_appointment_reminder_emails,
    send_medication_reminder_emails
)


class TestEmailService:
    """Test suite for EmailService."""
    
    @pytest.fixture
    def email_service(self):
        """Create EmailService instance."""
        return EmailService()
    
    def test_send_email_success(self, email_service):
        """Test sending a simple email."""
        result = email_service.send_email(
            to_email="patient@example.com",
            subject="Test Email",
            message="This is a test message"
        )
        
        assert result['success'] is True
        assert result['recipient'] == "patient@example.com"
        assert result['subject'] == "Test Email"
        assert 'timestamp' in result
        
        # Check email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["patient@example.com"]
        assert mail.outbox[0].subject == "Test Email"
    
    def test_send_email_with_html(self, email_service):
        """Test sending email with HTML content."""
        html_content = "<html><body><h1>Test</h1></body></html>"
        result = email_service.send_email(
            to_email="patient@example.com",
            subject="HTML Email",
            message="Plain text version",
            html_message=html_content
        )
        
        assert result['success'] is True
        assert len(mail.outbox) == 1
        
        # Check HTML alternative
        email = mail.outbox[0]
        assert len(email.alternatives) == 1
        assert email.alternatives[0][1] == "text/html"
    
    def test_send_bulk_email_success(self, email_service):
        """Test sending bulk emails."""
        recipients = [
            "patient1@example.com",
            "patient2@example.com",
            "patient3@example.com"
        ]
        
        result = email_service.send_bulk_email(
            recipients=recipients,
            subject="Bulk Email",
            message="Bulk message content"
        )
        
        assert result['success'] is True
        assert result['total'] == 3
        assert result['sent'] == 3
        assert result['failed'] == 0
        assert len(mail.outbox) == 3
    
    def test_send_appointment_reminder_email(self, email_service):
        """Test sending appointment reminder email."""
        result = email_service.send_appointment_reminder_email(
            patient_email="patient@example.com",
            patient_name="John Doe",
            appointment_date="2026-01-25",
            appointment_time="10:00 AM",
            hospital_name="Kigali Hospital",
            provider_name="Dr. Smith",
            appointment_type="Follow-up"
        )
        
        assert result['success'] is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert "Appointment Reminder" in email.subject
        assert "John Doe" in email.body
        assert "Kigali Hospital" in email.body
        assert "Dr. Smith" in email.body
    
    def test_send_medication_reminder_email(self, email_service):
        """Test sending medication reminder email."""
        result = email_service.send_medication_reminder_email(
            patient_email="patient@example.com",
            patient_name="Jane Doe",
            medication_name="Amoxicillin",
            dosage="500mg",
            timing="Twice daily",
            instructions="Take with food"
        )
        
        assert result['success'] is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert "Medication Reminder" in email.subject
        assert "Amoxicillin" in email.body
        assert "500mg" in email.body
        assert "Twice daily" in email.body
    
    def test_send_discharge_summary_email(self, email_service):
        """Test sending discharge summary email."""
        result = email_service.send_discharge_summary_email(
            patient_email="patient@example.com",
            patient_name="Bob Smith",
            hospital_name="Kigali Hospital",
            discharge_date="2026-01-20",
            diagnosis="Pneumonia - Recovered",
            follow_up_instructions="Rest for 2 weeks, take antibiotics"
        )
        
        assert result['success'] is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert "Discharge Summary" in email.subject
        assert "Bob Smith" in email.body
        assert "Pneumonia" in email.body
        assert "Rest for 2 weeks" in email.body


@pytest.mark.django_db
class TestEmailTasks:
    """Test suite for email-related Celery tasks."""
    
    @pytest.fixture(autouse=True)
    def setup_patients(self, django_user_model):
        """Set up test data."""
        from apps.patients.tests.factories import PatientFactory
        from apps.appointments.tests.factories import AppointmentFactory
        from apps.enrollment.tests.factories import HospitalFactory
        from apps.medications.models import Medication, Prescription
        
        self.hospital = HospitalFactory(name="Test Hospital")
        self.patient_with_email = PatientFactory(email="patient@example.com")
        self.patient_without_email = PatientFactory(email="")
        
        # Create upcoming appointment
        tomorrow = timezone.now() + timedelta(hours=12)
        self.appointment = AppointmentFactory(
            patient=self.patient_with_email,
            hospital=self.hospital,
            appointment_datetime=tomorrow,
            status='scheduled'
        )
        
        # Create medication and prescription manually
        self.medication = Medication.objects.create(
            name="Test Medication",
            generic_name="Test Generic",
            dosage_form="Tablet"
        )
        self.prescription = Prescription.objects.create(
            patient=self.patient_with_email,
            medication=self.medication,
            is_active=True,
            dosage="500mg",
            frequency='Twice daily',
            frequency_times_per_day=2,
            duration_days=7,
            start_date=timezone.now().date()
        )
    
    @patch('apps.messaging.tasks.send_email_notification_task.delay')
    def test_send_appointment_reminder_emails_task(self, mock_delay):
        """Test appointment reminder email task."""
        result = send_appointment_reminder_emails()
        
        assert result['sent'] >= 1
        assert mock_delay.called
        
        # Check that email task was called with correct data
        calls = mock_delay.call_args_list
        assert len(calls) >= 1
        
        # Verify context data
        call_args = calls[0][0]  # First call, positional args
        assert call_args[0] == "patient@example.com"
        assert call_args[1] == "appointment_reminder"
        assert 'patient_name' in call_args[2]
    
    @patch('apps.messaging.tasks.send_email_notification_task.delay')
    def test_send_medication_reminder_emails_task(self, mock_delay):
        """Test medication reminder email task."""
        result = send_medication_reminder_emails()
        
        assert result['sent'] >= 1
        assert mock_delay.called
        
        # Check that email task was called
        calls = mock_delay.call_args_list
        assert len(calls) >= 1
        
        call_args = calls[0][0]
        assert call_args[0] == "patient@example.com"
        assert call_args[1] == "medication_reminder"
    
    def test_send_email_notification_task_appointment(self):
        """Test send_email_notification_task for appointments."""
        context = {
            'patient_name': 'John Doe',
            'appointment_date': '2026-01-25',
            'appointment_time': '10:00 AM',
            'hospital_name': 'Test Hospital',
            'provider_name': 'Dr. Smith',
            'appointment_type': 'Follow-up'
        }
        
        result = send_email_notification_task(
            recipient_email="patient@example.com",
            notification_type="appointment_reminder",
            context_data=context
        )
        
        assert result['success'] is True
        assert len(mail.outbox) == 1
    
    def test_send_email_notification_task_medication(self):
        """Test send_email_notification_task for medications."""
        context = {
            'patient_name': 'Jane Doe',
            'medication_name': 'Amoxicillin',
            'dosage': '500mg',
            'timing': 'Twice daily',
            'instructions': 'Take with food'
        }
        
        result = send_email_notification_task(
            recipient_email="patient@example.com",
            notification_type="medication_reminder",
            context_data=context
        )
        
        assert result['success'] is True
        assert len(mail.outbox) == 1
    
    def test_send_email_notification_task_discharge(self):
        """Test send_email_notification_task for discharge summary."""
        context = {
            'patient_name': 'Bob Smith',
            'hospital_name': 'Test Hospital',
            'discharge_date': '2026-01-20',
            'diagnosis': 'Recovered',
            'follow_up_instructions': 'Rest and hydrate'
        }
        
        result = send_email_notification_task(
            recipient_email="patient@example.com",
            notification_type="discharge_summary",
            context_data=context
        )
        
        assert result['success'] is True
        assert len(mail.outbox) == 1
    
    def test_send_email_notification_task_invalid_type(self):
        """Test task with invalid notification type."""
        with pytest.raises(ValueError):
            send_email_notification_task(
                recipient_email="patient@example.com",
                notification_type="invalid_type",
                context_data={}
            )


@pytest.mark.django_db
class TestEmailServiceEdgeCases:
    """Test edge cases and error handling for email service."""
    
    @pytest.fixture
    def email_service(self):
        """Create EmailService instance."""
        return EmailService()
    
    @patch('apps.messaging.email_service.send_mail', side_effect=Exception("SMTP error"))
    def test_send_email_failure(self, mock_send, email_service):
        """Test email sending failure handling."""
        result = email_service.send_email(
            to_email="patient@example.com",
            subject="Test",
            message="Test"
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'SMTP error' in result['error']
    
    def test_send_bulk_email_partial_failure(self, email_service):
        """Test bulk email with some failures."""
        with patch('apps.messaging.email_service.send_mail') as mock_send:
            # First call succeeds, second fails, third succeeds
            mock_send.side_effect = [None, Exception("Failed"), None]
            
            result = email_service.send_bulk_email(
                recipients=["email1@test.com", "email2@test.com", "email3@test.com"],
                subject="Test",
                message="Test"
            )
            
            assert result['success'] is False  # Not all succeeded
            assert result['sent'] == 2
            assert result['failed'] == 1
            assert result['total'] == 3
