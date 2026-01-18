import pytest
from django.utils import timezone
from datetime import time, timedelta
from rest_framework.exceptions import ValidationError as DRFValidationError
from apps.medications.models import Medication, Prescription, MedicationAdherence
from apps.medications.serializers import (
    MedicationSerializer,
    PrescriptionListSerializer,
    PrescriptionDetailSerializer,
    PrescriptionCreateSerializer,
    MedicationAdherenceSerializer,
)
from apps.patients.tests.factories import PatientFactory
from apps.enrollment.models import Hospital, DischargeSummary


@pytest.mark.django_db
class TestMedicationSerializer:
    """Test suite for MedicationSerializer"""
    
    def test_serialize_medication(self):
        """Test serializing a medication"""
        medication = Medication.objects.create(
            name='Paracetamol 500mg',
            generic_name='Paracetamol',
            brand_name='Panadol',
            dosage_form='tablet',
            strength='500mg',
            manufacturer='GSK',
            requires_prescription=False,
            is_active=True
        )
        
        serializer = MedicationSerializer(medication)
        data = serializer.data
        
        assert data['id'] == medication.id
        assert data['name'] == 'Paracetamol 500mg'
        assert data['generic_name'] == 'Paracetamol'
        assert data['brand_name'] == 'Panadol'
        assert data['dosage_form'] == 'tablet'
        assert data['strength'] == '500mg'
        assert data['manufacturer'] == 'GSK'
        assert data['requires_prescription'] is False
        assert data['is_active'] is True
    
    def test_deserialize_medication(self):
        """Test deserializing and creating a medication"""
        data = {
            'name': 'Ibuprofen 400mg',
            'generic_name': 'Ibuprofen',
            'dosage_form': 'tablet',
            'strength': '400mg',
            'requires_prescription': False
        }
        
        serializer = MedicationSerializer(data=data)
        assert serializer.is_valid()
        medication = serializer.save()
        
        assert medication.name == 'Ibuprofen 400mg'
        assert medication.generic_name == 'Ibuprofen'
        assert medication.dosage_form == 'tablet'
        assert medication.strength == '400mg'
    
    def test_medication_validation_required_fields(self):
        """Test that required fields are validated"""
        data = {
            'name': 'Test Med'
            # Missing generic_name, dosage_form, strength
        }
        
        serializer = MedicationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'generic_name' in serializer.errors
        assert 'dosage_form' in serializer.errors
        assert 'strength' in serializer.errors


@pytest.mark.django_db
class TestPrescriptionSerializers:
    """Test suite for Prescription serializers"""
    
    def test_prescription_list_serializer(self):
        """Test PrescriptionListSerializer"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Amoxicillin 500mg',
            generic_name='Amoxicillin',
            dosage_form='capsule',
            strength='500mg'
        )
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='500mg',
            frequency='3 times daily',
            frequency_times_per_day=3,
            duration_days=7,
            start_date=timezone.now().date()
        )
        
        serializer = PrescriptionListSerializer(prescription)
        data = serializer.data
        
        assert data['id'] == prescription.id
        assert 'patient_name' in data
        assert 'medication_name' in data
        assert data['dosage'] == '500mg'
        assert data['frequency'] == '3 times daily'
    
    def test_prescription_detail_serializer(self):
        """Test PrescriptionDetailSerializer with nested data"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Amoxicillin 500mg',
            generic_name='Amoxicillin',
            dosage_form='capsule',
            strength='500mg'
        )
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='500mg',
            frequency='3 times daily',
            frequency_times_per_day=3,
            duration_days=7
        )
        
        serializer = PrescriptionDetailSerializer(prescription)
        data = serializer.data
        
        assert data['id'] == prescription.id
        assert 'patient' in data
        assert 'medication' in data
        assert isinstance(data['patient'], dict)
        assert isinstance(data['medication'], dict)
    
    def test_prescription_create_serializer(self):
        """Test creating a prescription"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        
        data = {
            'patient': patient.id,
            'medication': medication.id,
            'dosage': '100mg',
            'frequency': 'twice daily',
            'frequency_times_per_day': 2,
            'duration_days': 5,
            'route': 'oral'
        }
        
        serializer = PrescriptionCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        prescription = serializer.save()
        
        assert prescription.patient == patient
        assert prescription.medication == medication
        assert prescription.dosage == '100mg'
        assert prescription.frequency_times_per_day == 2
    
    def test_prescription_validation_required_fields(self):
        """Test prescription required field validation"""
        data = {
            'dosage': '100mg'
            # Missing patient, medication, frequency, etc.
        }
        
        serializer = PrescriptionCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'patient' in serializer.errors
        assert 'medication' in serializer.errors
        assert 'frequency' in serializer.errors


@pytest.mark.django_db
class TestMedicationAdherenceSerializer:
    """Test suite for MedicationAdherenceSerializer"""
    
    def test_serialize_adherence_record(self):
        """Test serializing an adherence record"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7
        )
        adherence = MedicationAdherence.objects.create(
            prescription=prescription,
            patient=patient,
            scheduled_time=time(8, 0),
            status='taken',
            taken_at=timezone.now()
        )
        
        serializer = MedicationAdherenceSerializer(adherence)
        data = serializer.data
        
        assert data['id'] == adherence.id
        assert data['status'] == 'taken'
        assert 'prescription' in data
        assert 'patient' in data
    
    def test_create_adherence_record(self):
        """Test creating an adherence record"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7
        )
        
        data = {
            'prescription': prescription.id,
            'patient': patient.id,
            'scheduled_time': '08:00:00',
            'status': 'scheduled'
        }
        
        serializer = MedicationAdherenceSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        adherence = serializer.save()
        
        assert adherence.prescription == prescription
        assert adherence.patient == patient
        assert adherence.status == 'scheduled'
