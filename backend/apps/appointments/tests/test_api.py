"""
Tests for appointments API endpoints.
Following TDD: Write tests first, then implement views.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment, AppointmentReminder
from apps.patients.models import Patient
from apps.enrollment.models import Hospital


@pytest.fixture
def sample_patient():
    """Create a sample patient."""
    return Patient.objects.create(
        first_name="Test",
        last_name="Patient",
        national_id="1199012345678901",
        date_of_birth="1990-01-01",
        gender="M",
        phone_number="+250788987654"
    )


@pytest.fixture
def sample_hospital():
    """Create a sample hospital."""
    return Hospital.objects.create(
        name="Test Hospital",
        code="TH001",
        hospital_type="district",
        phone_number="+250788123456",
        province="Kigali",
        district="Gasabo"
    )


@pytest.mark.django_db
class TestAppointmentAPI:
    """Test Appointment API endpoints."""
    
    def test_list_appointments(self, authenticated_client, sample_patient, sample_hospital):
        """Test listing appointments."""
        Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        response = authenticated_client.get('/api/v1/appointments/')
        assert response.status_code == 200
        assert response.data['count'] == 1
        
    def test_create_appointment(self, authenticated_client, sample_patient, sample_hospital):
        """Test creating an appointment."""
        future_datetime = timezone.now() + timedelta(days=2)
        data = {
            'patient': sample_patient.id,
            'hospital': sample_hospital.id,
            'appointment_datetime': future_datetime.isoformat(),
            'appointment_type': 'follow_up',
            'status': 'scheduled',
            'location_type': 'hospital'
        }
        
        response = authenticated_client.post('/api/v1/appointments/', data)
        assert response.status_code == 201
        assert Appointment.objects.count() == 1
        
    def test_retrieve_appointment(self, authenticated_client, sample_patient, sample_hospital):
        """Test retrieving a single appointment."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        response = authenticated_client.get(f'/api/v1/appointments/{appointment.id}/')
        assert response.status_code == 200
        assert response.data['id'] == appointment.id
        
    def test_update_appointment(self, authenticated_client, sample_patient, sample_hospital):
        """Test updating an appointment."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        data = {
            'patient': sample_patient.id,
            'hospital': sample_hospital.id,
            'appointment_datetime': appointment.appointment_datetime.isoformat(),
            'appointment_type': 'consultation',
            'status': 'confirmed'
        }
        
        response = authenticated_client.put(f'/api/v1/appointments/{appointment.id}/', data)
        assert response.status_code == 200
        appointment.refresh_from_db()
        assert appointment.status == 'confirmed'
        
    def test_filter_appointments_by_status(self, authenticated_client, sample_patient, sample_hospital):
        """Test filtering appointments by status."""
        Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=2),
            appointment_type="follow_up",
            status="confirmed"
        )
        
        response = authenticated_client.get('/api/v1/appointments/?status=scheduled')
        assert response.status_code == 200
        assert response.data['count'] == 1
        
    def test_filter_appointments_by_patient(self, authenticated_client, sample_hospital):
        """Test filtering appointments by patient."""
        patient1 = Patient.objects.create(
            first_name="Patient",
            last_name="One",
            national_id="1199012345678902",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987655"
        )
        patient2 = Patient.objects.create(
            first_name="Patient",
            last_name="Two",
            national_id="1199012345678903",
            date_of_birth="1990-01-01",
            gender="F",
            phone_number="+250788987656"
        )
        
        Appointment.objects.create(
            patient=patient1,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        Appointment.objects.create(
            patient=patient2,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=2),
            appointment_type="follow_up",
            status="scheduled"
        )
        
        response = authenticated_client.get(f'/api/v1/appointments/?patient={patient1.id}')
        assert response.status_code == 200
        assert response.data['count'] == 1


@pytest.mark.django_db
class TestAppointmentCustomActions:
    """Test custom actions on Appointment viewset."""
    
    def test_upcoming_appointments(self, authenticated_client, sample_patient, sample_hospital):
        """Test getting upcoming appointments."""
        # Future appointment
        Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        # Past appointment
        Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() - timedelta(days=1),
            appointment_type="follow_up",
            status="completed"
        )
        
        response = authenticated_client.get('/api/v1/appointments/upcoming/')
        assert response.status_code == 200
        assert response.data['count'] == 1
        
    def test_confirm_appointment(self, authenticated_client, sample_patient, sample_hospital):
        """Test confirming an appointment."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        response = authenticated_client.post(f'/api/v1/appointments/{appointment.id}/confirm/')
        assert response.status_code == 200
        appointment.refresh_from_db()
        assert appointment.status == 'confirmed'
        
    def test_cancel_appointment(self, authenticated_client, sample_patient, sample_hospital):
        """Test cancelling an appointment."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        response = authenticated_client.post(f'/api/v1/appointments/{appointment.id}/cancel/')
        assert response.status_code == 200
        appointment.refresh_from_db()
        assert appointment.status == 'cancelled'
        
    def test_complete_appointment(self, authenticated_client, sample_patient, sample_hospital):
        """Test marking appointment as complete."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() - timedelta(hours=1),
            appointment_type="consultation",
            status="confirmed"
        )
        
        response = authenticated_client.post(f'/api/v1/appointments/{appointment.id}/complete/')
        assert response.status_code == 200
        appointment.refresh_from_db()
        assert appointment.status == 'completed'


@pytest.mark.django_db
class TestAppointmentReminderAPI:
    """Test AppointmentReminder API endpoints."""
    
    def test_list_reminders(self, authenticated_client, sample_patient, sample_hospital):
        """Test listing reminders."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        
        response = authenticated_client.get('/api/v1/appointment-reminders/')
        assert response.status_code == 200
        assert response.data['count'] == 1
        
    def test_create_reminder(self, authenticated_client, sample_patient, sample_hospital):
        """Test creating a reminder."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        reminder_datetime = timezone.now() + timedelta(hours=23)
        data = {
            'appointment': appointment.id,
            'reminder_datetime': reminder_datetime.isoformat(),
            'reminder_type': 'whatsapp',
            'status': 'pending'
        }
        
        response = authenticated_client.post('/api/v1/appointment-reminders/', data)
        assert response.status_code == 201
        assert AppointmentReminder.objects.count() == 1
        
    def test_filter_reminders_by_status(self, authenticated_client, sample_patient, sample_hospital):
        """Test filtering reminders by status."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            hospital=sample_hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=2),
            reminder_type="whatsapp",
            status="sent"
        )
        
        response = authenticated_client.get('/api/v1/appointment-reminders/?status=pending')
        assert response.status_code == 200
        assert response.data['count'] == 1
