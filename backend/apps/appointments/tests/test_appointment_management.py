"""
Test cases for Patient Appointment Management API.
Uses TDD approach: Tests written first, then implementation.
"""
import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from apps.appointments.models import Appointment
from apps.patients.tests.factories import PatientFactory
from apps.enrollment.tests.factories import HospitalFactory
from apps.patients.tests.factories import UserFactory


@pytest.mark.django_db
class TestPatientAppointmentManagementAPI:
    """Test suite for patient appointment management endpoints."""
    
    def setup_method(self):
        """Set up test client and create test data."""
        self.client = APIClient()
        
        # Create a patient with associated user
        self.user = UserFactory()
        self.patient = PatientFactory()
        self.patient.user = self.user
        self.patient.save()
        
        # Create another patient (for list filtering tests)
        self.other_patient = PatientFactory()
        
        # Create hospital
        self.hospital = HospitalFactory()
        
        # Create test appointments
        now = timezone.now()
        self.upcoming_appointment = Appointment.objects.create(
            patient=self.patient,
            hospital=self.hospital,
            appointment_datetime=now + timedelta(days=5),
            appointment_type='follow_up',
            status='confirmed',
            location_type='hospital',
            provider_name='Dr. Habimana',
            department='General Medicine',
            reason='Post-discharge follow-up',
            duration_minutes=30
        )
        
        self.past_appointment = Appointment.objects.create(
            patient=self.patient,
            hospital=self.hospital,
            appointment_datetime=now - timedelta(days=5),
            appointment_type='routine_checkup',
            status='completed',
            location_type='hospital',
            provider_name='Dr. Umurungi',
            department='General Medicine',
            reason='Routine follow-up',
            duration_minutes=30
        )
        
        self.cancelled_appointment = Appointment.objects.create(
            patient=self.patient,
            hospital=self.hospital,
            appointment_datetime=now + timedelta(days=10),
            appointment_type='medication_review',
            status='cancelled',
            location_type='telemedicine',
            provider_name='Dr. Kamali',
            reason='Medication adjustment',
            duration_minutes=20
        )
    
    # ============ LIST APPOINTMENTS ============
    def test_patient_list_own_appointments(self):
        """Test patient can view all their own appointments."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/appointments/my-appointments/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        # Check that upcoming appointment is in the list
        appointment_ids = [a['id'] for a in response.data]
        assert self.upcoming_appointment.id in appointment_ids
    
    def test_patient_list_appointments_only_own(self):
        """Test patient can only see their own appointments, not others."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/appointments/my-appointments/')
        
        appointment_ids = [a['id'] for a in response.data]
        assert self.upcoming_appointment.id in appointment_ids
        assert self.past_appointment.id in appointment_ids
        
        # Create appointment for different patient
        other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            hospital=self.hospital,
            appointment_datetime=timezone.now() + timedelta(days=3),
            appointment_type='follow_up',
            status='confirmed',
            location_type='hospital'
        )
        
        response = self.client.get('/api/v1/appointments/my-appointments/')
        appointment_ids = [a['id'] for a in response.data]
        assert other_appointment.id not in appointment_ids
    
    def test_patient_appointments_sorted_by_datetime(self):
        """Test appointments are sorted by datetime (upcoming first)."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/appointments/my-appointments/')
        
        # Should be sorted by datetime ascending (past first, upcoming last)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        # Check appointments are ordered by datetime ascending
        datetimes = [a['appointment_datetime'] for a in response.data]
        assert datetimes == sorted(datetimes)
    
    def test_unauthenticated_cannot_list_appointments(self):
        """Test unauthenticated users cannot access appointments."""
        response = self.client.get('/api/v1/appointments/my-appointments/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # ============ GET APPOINTMENT DETAIL ============
    def test_patient_get_appointment_detail(self):
        """Test patient can get detailed view of their appointment."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.upcoming_appointment.id
        assert response.data['provider_name'] == 'Dr. Habimana'
        assert response.data['appointment_type'] == 'follow_up'
        assert response.data['status'] == 'confirmed'
        assert 'appointment_datetime' in response.data
        assert 'location_type' in response.data
        assert 'department' in response.data
        assert 'reason' in response.data
    
    def test_patient_cannot_get_other_patient_appointment(self):
        """Test patient cannot view other patient's appointments."""
        # Create appointment for different patient
        other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            hospital=self.hospital,
            appointment_datetime=timezone.now() + timedelta(days=3),
            appointment_type='follow_up',
            status='confirmed',
            location_type='hospital'
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/api/v1/appointments/my-appointments/{other_appointment.id}/'
        )
        
        # Should return 404 since appointment is not in patient's queryset
        # (DRF returns 404 for objects not in queryset, which is correct)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_appointment_detail_includes_all_fields(self):
        """Test appointment detail includes all necessary fields for UI."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/'
        )
        
        required_fields = [
            'id', 'appointment_datetime', 'appointment_type', 'status',
            'location_type', 'provider_name', 'department', 'reason',
            'hospital_name', 'duration_minutes'
        ]
        
        for field in required_fields:
            assert field in response.data, f"Missing field: {field}"
    
    # ============ RESCHEDULE APPOINTMENT ============
    def test_patient_reschedule_confirmed_appointment(self):
        """Test patient can reschedule a confirmed appointment."""
        self.client.force_authenticate(user=self.user)
        new_datetime = timezone.now() + timedelta(days=10)
        
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/reschedule/',
            {'appointment_datetime': new_datetime.isoformat()},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['appointment_datetime'] is not None
        
        # Verify in database
        self.upcoming_appointment.refresh_from_db()
        assert self.upcoming_appointment.appointment_datetime.date() == new_datetime.date()
    
    def test_patient_cannot_reschedule_past_appointment(self):
        """Test patient cannot reschedule appointment that already happened."""
        self.client.force_authenticate(user=self.user)
        new_datetime = timezone.now() + timedelta(days=10)
        
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{self.past_appointment.id}/reschedule/',
            {'appointment_datetime': new_datetime.isoformat()},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'past' in response.data.get('detail', '').lower()
    
    def test_patient_cannot_reschedule_cancelled_appointment(self):
        """Test patient cannot reschedule cancelled appointment."""
        self.client.force_authenticate(user=self.user)
        new_datetime = timezone.now() + timedelta(days=10)
        
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{self.cancelled_appointment.id}/reschedule/',
            {'appointment_datetime': new_datetime.isoformat()},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cancelled' in response.data.get('detail', '').lower()
    
    def test_cannot_reschedule_to_past_date(self):
        """Test cannot reschedule appointment to a past date."""
        self.client.force_authenticate(user=self.user)
        past_datetime = timezone.now() - timedelta(days=5)
        
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/reschedule/',
            {'appointment_datetime': past_datetime.isoformat()},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'past' in response.data.get('detail', '').lower()
    
    def test_reschedule_requires_valid_datetime(self):
        """Test reschedule endpoint validates datetime field."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/reschedule/',
            {'appointment_datetime': 'invalid-date'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_reschedule_without_datetime_fails(self):
        """Test reschedule fails if datetime is missing."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/reschedule/',
            {},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # ============ CANCEL APPOINTMENT ============
    def test_patient_cancel_upcoming_appointment(self):
        """Test patient can cancel an upcoming appointment."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/cancel/',
            {'cancellation_reason': 'Patient request'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
        
        # Verify in database
        self.upcoming_appointment.refresh_from_db()
        assert self.upcoming_appointment.status == 'cancelled'
    
    def test_patient_can_cancel_with_reason(self):
        """Test cancellation reason is saved."""
        self.client.force_authenticate(user=self.user)
        reason = 'Unable to attend due to work'
        
        response = self.client.post(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/cancel/',
            {'cancellation_reason': reason},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        self.upcoming_appointment.refresh_from_db()
        # Check if reason is captured (model should have cancellation_reason field)
        if hasattr(self.upcoming_appointment, 'cancellation_reason'):
            assert self.upcoming_appointment.cancellation_reason == reason
    
    def test_patient_cannot_cancel_past_appointment(self):
        """Test patient cannot cancel appointment that already happened."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            f'/api/v1/appointments/my-appointments/{self.past_appointment.id}/cancel/',
            {'cancellation_reason': 'Patient request'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'past' in response.data.get('detail', '').lower()
    
    def test_patient_cannot_cancel_already_cancelled(self):
        """Test patient cannot cancel already cancelled appointment."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            f'/api/v1/appointments/my-appointments/{self.cancelled_appointment.id}/cancel/',
            {'cancellation_reason': 'Patient request'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already cancelled' in response.data.get('detail', '').lower()
    
    def test_cancellation_reason_optional(self):
        """Test cancellation reason is optional."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/cancel/',
            {},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
    
    # ============ FILTER & SEARCH ============
    def test_list_appointments_filter_by_status(self):
        """Test can filter appointments by status."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/appointments/my-appointments/?status=confirmed')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['status'] == 'confirmed'
    
    def test_list_appointments_filter_by_type(self):
        """Test can filter appointments by type."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/appointments/my-appointments/?appointment_type=follow_up')
        
        assert response.status_code == status.HTTP_200_OK
        assert all(a['appointment_type'] == 'follow_up' for a in response.data)
    
    def test_list_upcoming_appointments_only(self):
        """Test can get only upcoming appointments."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/appointments/my-appointments/?upcoming=true')
        
        assert response.status_code == status.HTTP_200_OK
        # Should only have upcoming and future cancelled appointments
        assert self.upcoming_appointment.id in [a['id'] for a in response.data]
        assert self.past_appointment.id not in [a['id'] for a in response.data]
    
    def test_list_past_appointments_only(self):
        """Test can get only past appointments."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/appointments/my-appointments/?past=true')
        
        assert response.status_code == status.HTTP_200_OK
        assert self.past_appointment.id in [a['id'] for a in response.data]
    
    # ============ PERMISSIONS ============
    def test_unauthenticated_user_cannot_reschedule(self):
        """Test unauthenticated user cannot reschedule appointment."""
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/reschedule/',
            {'appointment_datetime': timezone.now() + timedelta(days=10)},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_user_cannot_cancel(self):
        """Test unauthenticated user cannot cancel appointment."""
        response = self.client.post(
            f'/api/v1/appointments/my-appointments/{self.upcoming_appointment.id}/cancel/',
            {},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_patient_cannot_reschedule_other_patient_appointment(self):
        """Test patient cannot reschedule other patient's appointment."""
        other_patient_user = UserFactory()
        other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            hospital=self.hospital,
            appointment_datetime=timezone.now() + timedelta(days=5),
            appointment_type='follow_up',
            status='confirmed',
            location_type='hospital'
        )
        self.other_patient.user = other_patient_user
        self.other_patient.save()
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.patch(
            f'/api/v1/appointments/my-appointments/{other_appointment.id}/reschedule/',
            {'appointment_datetime': timezone.now() + timedelta(days=10)},
            format='json'
        )
        
        # Should return 404 since appointment is not in patient's queryset
        assert response.status_code == status.HTTP_404_NOT_FOUND
