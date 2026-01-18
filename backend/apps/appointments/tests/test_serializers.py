"""
Tests for appointment serializers.
Following TDD: Write tests first, then implement serializers.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment, AppointmentReminder
from apps.appointments.serializers import (
    AppointmentSerializer,
    AppointmentListSerializer,
    AppointmentDetailSerializer,
    AppointmentCreateSerializer,
    AppointmentReminderSerializer
)
from apps.patients.models import Patient
from apps.enrollment.models import Hospital


@pytest.mark.django_db
class TestAppointmentSerializer:
    """Test AppointmentSerializer."""
    
    def test_serialize_appointment(self):
        """Test serializing an appointment."""
        patient = Patient.objects.create(
            first_name="Jean",
            last_name="Mugabo",
            national_id="1199012345678901",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987654"
        )
        hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TH001",
            hospital_type="district",
            phone_number="+250788123456",
            province="Kigali",
            district="Gasabo"
        )
        
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="follow_up",
            status="scheduled"
        )
        
        serializer = AppointmentSerializer(appointment)
        data = serializer.data
        
        assert data['id'] == appointment.id
        assert data['appointment_type'] == 'follow_up'
        assert data['status'] == 'scheduled'
        
    def test_appointment_validation_required_fields(self):
        """Test validation of required fields."""
        serializer = AppointmentSerializer(data={})
        assert not serializer.is_valid()
        assert 'patient' in serializer.errors
        assert 'hospital' in serializer.errors
        assert 'appointment_datetime' in serializer.errors
        assert 'appointment_type' in serializer.errors


@pytest.mark.django_db
class TestAppointmentListSerializer:
    """Test AppointmentListSerializer."""
    
    def test_list_serializer_includes_patient_name(self):
        """Test list serializer includes patient full name."""
        patient = Patient.objects.create(
            first_name="Jean",
            last_name="Mugabo",
            national_id="1199012345678902",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987655"
        )
        hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TH002",
            hospital_type="district",
            phone_number="+250788123457",
            province="Kigali",
            district="Gasabo"
        )
        
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        serializer = AppointmentListSerializer(appointment)
        data = serializer.data
        
        assert 'patient_name' in data
        assert data['patient_name'] == "Jean Mugabo"
        assert 'hospital_name' in data
        assert data['hospital_name'] == "Test Hospital"


@pytest.mark.django_db
class TestAppointmentDetailSerializer:
    """Test AppointmentDetailSerializer."""
    
    def test_detail_serializer_includes_nested_data(self):
        """Test detail serializer includes nested patient and hospital data."""
        patient = Patient.objects.create(
            first_name="Jean",
            last_name="Mugabo",
            national_id="1199012345678903",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987656"
        )
        hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TH003",
            hospital_type="district",
            phone_number="+250788123458",
            province="Kigali",
            district="Gasabo"
        )
        
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="medication_review",
            status="confirmed",
            provider_name="Dr. Mutesi"
        )
        
        serializer = AppointmentDetailSerializer(appointment)
        data = serializer.data
        
        assert 'patient' in data
        assert 'hospital' in data
        assert data['provider_name'] == "Dr. Mutesi"
        assert 'is_upcoming' in data
        assert 'is_overdue' in data


@pytest.mark.django_db
class TestAppointmentCreateSerializer:
    """Test AppointmentCreateSerializer."""
    
    def test_create_appointment_via_serializer(self):
        """Test creating appointment through serializer."""
        patient = Patient.objects.create(
            first_name="Create",
            last_name="Test",
            national_id="1199012345678904",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987657"
        )
        hospital = Hospital.objects.create(
            name="Create Hospital",
            code="CH001",
            hospital_type="district",
            phone_number="+250788123459",
            province="Kigali",
            district="Gasabo"
        )
        
        future_datetime = timezone.now() + timedelta(days=1)
        data = {
            'patient': patient.id,
            'hospital': hospital.id,
            'appointment_datetime': future_datetime.isoformat(),
            'appointment_type': 'consultation',
            'status': 'scheduled'
        }
        
        serializer = AppointmentCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        appointment = serializer.save()
        
        assert appointment.patient == patient
        assert appointment.hospital == hospital
        assert appointment.appointment_type == 'consultation'


@pytest.mark.django_db
class TestAppointmentReminderSerializer:
    """Test AppointmentReminderSerializer."""
    
    def test_serialize_reminder(self):
        """Test serializing a reminder."""
        patient = Patient.objects.create(
            first_name="Reminder",
            last_name="Test",
            national_id="1199012345678905",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987658"
        )
        hospital = Hospital.objects.create(
            name="Reminder Hospital",
            code="RH001",
            hospital_type="district",
            phone_number="+250788123460",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        
        serializer = AppointmentReminderSerializer(reminder)
        data = serializer.data
        
        assert data['id'] == reminder.id
        assert data['reminder_type'] == 'sms'
        assert data['status'] == 'pending'
        assert 'is_due' in data
        
    def test_create_reminder_via_serializer(self):
        """Test creating reminder through serializer."""
        patient = Patient.objects.create(
            first_name="Create",
            last_name="Reminder",
            national_id="1199012345678906",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987659"
        )
        hospital = Hospital.objects.create(
            name="Create Hospital",
            code="CRH001",
            hospital_type="district",
            phone_number="+250788123461",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
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
        
        serializer = AppointmentReminderSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        reminder = serializer.save()
        
        assert reminder.appointment == appointment
        assert reminder.reminder_type == 'whatsapp'
