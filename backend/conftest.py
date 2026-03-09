"""
Pytest configuration and fixtures for bicare360 tests.
"""
import os
import django

# Configure Django settings before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

import pytest
from datetime import time, date, timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def authenticated_client(db, api_client):
    """Return an authenticated API client."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def authenticated_admin_client(db, api_client, admin_user):
    """Return an authenticated API client with admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Automatically enable database access for all tests."""
    pass


# Medication & Prescription Factories

@pytest.fixture
def medication_factory(db):
    """Factory for creating medications"""
    from apps.medications.models import Medication
    
    def create_medication(**kwargs):
        defaults = {
            'name': 'Paracetamol',
            'generic_name': 'Acetaminophen',
            'dosage_form': 'tablet',
            'strength': '500mg',
            'requires_prescription': False,
        }
        defaults.update(kwargs)
        return Medication.objects.create(**defaults)
    
    return create_medication


@pytest.fixture
def prescription_factory(db, patient_factory, medication_factory):
    """Factory for creating prescriptions"""
    from apps.medications.models import Prescription
    
    def create_prescription(**kwargs):
        if 'patient' not in kwargs:
            kwargs['patient'] = patient_factory()
        if 'medication' not in kwargs:
            kwargs['medication'] = medication_factory()
        
        defaults = {
            'dosage': '500mg',
            'frequency': 'twice_daily',
            'frequency_times_per_day': 2,
            'route': 'oral',
            'duration_days': 7,
            'start_date': date.today(),
        }
        defaults.update(kwargs)
        return Prescription.objects.create(**defaults)
    
    return create_prescription


@pytest.fixture
def adherence_factory(db, prescription_factory):
    """Factory for creating medication adherence records"""
    from apps.medications.models import MedicationAdherence
    
    def create_adherence(**kwargs):
        if 'prescription' not in kwargs:
            prescription = prescription_factory()
            kwargs['prescription'] = prescription
            kwargs.setdefault('patient', prescription.patient)
        
        defaults = {
            'scheduled_date': date.today(),
            'scheduled_time': time(9, 0),
            'status': 'scheduled',
        }
        defaults.update(kwargs)
        return MedicationAdherence.objects.create(**defaults)
    
    # Add batch creation method
    def create_batch(size, **kwargs):
        return [create_adherence(**kwargs) for _ in range(size)]
    
    create_adherence.create_batch = create_batch
    return create_adherence


@pytest.fixture
def patient_factory(db):
    """Factory for creating patients"""
    from apps.patients.models import Patient
    
    counter = {'value': 0}
    
    def create_patient(**kwargs):
        counter['value'] += 1
        defaults = {
            'national_id': f'119980012345{counter["value"]:02d}',
            'first_name': f'Test{counter["value"]}',
            'last_name': f'Patient{counter["value"]}',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'M',
            'phone_number': f'+25078000000{counter["value"]:02d}',
            'is_active': True,
        }
        defaults.update(kwargs)
        return Patient.objects.create(**defaults)
    
    return create_patient
