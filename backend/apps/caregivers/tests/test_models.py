"""
Tests for Caregiver models.
Following TDD approach - tests written first.
"""
import pytest
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from apps.caregivers.models import (
    Caregiver, CaregiverService, CaregiverCertification,
    CaregiverBooking, CaregiverReview
)
from apps.patients.models import Patient


@pytest.mark.django_db
class TestCaregiverModel:
    
    def test_create_caregiver(self):
        """Test creating a caregiver with required fields."""
        caregiver = Caregiver.objects.create(
            first_name='Sarah',
            last_name='Johnson',
            email='sarah@example.com',
            phone_number='+250788123456',
            profession='registered_nurse',
            experience_years=5,
            bio='Experienced RN',
            province='Kigali',
            district='Gasabo',
            hourly_rate=45.00
        )
        assert caregiver.full_name == 'Sarah Johnson'
        assert caregiver.rating == 0.0
        assert caregiver.is_active is True
    
    def test_caregiver_phone_validation(self):
        """Test phone number validation."""
        with pytest.raises(ValidationError):
            caregiver = Caregiver(
                first_name='Test',
                last_name='User',
                email='test@example.com',
                phone_number='123456',  # Invalid
                profession='registered_nurse',
                experience_years=5,
                bio='Test',
                province='Kigali',
                district='Gasabo',
                hourly_rate=45.00
            )
            caregiver.full_clean()


@pytest.mark.django_db
class TestCaregiverBooking:
    
    def test_create_booking(self, patient_factory, caregiver_factory):
        """Test creating a caregiver booking."""
        patient = patient_factory()
        caregiver = caregiver_factory()
        
        booking = CaregiverBooking.objects.create(
            patient=patient,
            caregiver=caregiver,
            service_type='Home Care',
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=4),
            duration_hours=4.0,
            location_address='Kigali, Gasabo',
            hourly_rate=45.00,
            total_cost=180.00
        )
        assert booking.status == 'pending'
        assert booking.total_cost == 180.00
