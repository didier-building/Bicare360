"""
Unit tests for enrollment serializers.
"""
import pytest
from datetime import date
from django.contrib.auth import get_user_model
from apps.enrollment.serializers import (
    HospitalSerializer,
    DischargeSummaryListSerializer,
    DischargeSummaryDetailSerializer,
    DischargeSummaryCreateSerializer
)
from apps.enrollment.tests.factories import HospitalFactory, DischargeSummaryFactory
from apps.patients.tests.factories import PatientFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestHospitalSerializer:
    """Test HospitalSerializer."""
    
    def test_serialize_hospital(self):
        """Test serializing a hospital."""
        hospital = HospitalFactory(
            name="Kigali Hospital",
            code="KH01",
            hospital_type="referral"
        )
        serializer = HospitalSerializer(hospital)
        data = serializer.data
        
        assert data['name'] == "Kigali Hospital"
        assert data['code'] == "KH01"
        assert data['hospital_type'] == "referral"
        assert 'id' in data
        assert 'created_at' in data
    
    def test_deserialize_hospital(self):
        """Test deserializing hospital data."""
        data = {
            'name': 'New Hospital',
            'code': 'NH01',
            'hospital_type': 'district',
            'province': 'Kigali',
            'district': 'Gasabo',
            'phone_number': '+250788123456',
            'status': 'active'
        }
        serializer = HospitalSerializer(data=data)
        assert serializer.is_valid()
        hospital = serializer.save()
        assert hospital.name == 'New Hospital'
        assert hospital.code == 'NH01'


@pytest.mark.django_db
class TestDischargeSummaryListSerializer:
    """Test DischargeSummaryListSerializer."""
    
    def test_serialize_discharge_summary_list(self):
        """Test serializing discharge summary for list view."""
        patient = PatientFactory(first_name="John", last_name="Doe")
        hospital = HospitalFactory(name="Test Hospital", code="TH01")
        discharge = DischargeSummaryFactory(
            patient=patient,
            hospital=hospital,
            risk_level="high"
        )
        
        serializer = DischargeSummaryListSerializer(discharge)
        data = serializer.data
        
        assert "John Doe" in data['patient']['full_name']
        assert data['hospital_name'] == "Test Hospital"
        assert data['hospital_code'] == "TH01"
        assert data['risk_level'] == "high"
        assert data['is_high_risk'] is True
        assert 'primary_diagnosis' in data
        assert 'discharge_condition' in data


@pytest.mark.django_db
class TestDischargeSummaryDetailSerializer:
    """Test DischargeSummaryDetailSerializer."""
    
    def test_serialize_discharge_summary_detail(self):
        """Test serializing discharge summary with all fields."""
        user = UserFactory(first_name="Dr.", last_name="Smith")
        discharge = DischargeSummaryFactory(
            primary_diagnosis="Hypertension",
            discharge_instructions="Take medication daily",
            discharge_instructions_kinyarwanda="Mfata umuti buri gihe",
            created_by=user
        )
        
        serializer = DischargeSummaryDetailSerializer(discharge)
        data = serializer.data
        
        assert data['primary_diagnosis'] == "Hypertension"
        assert data['discharge_instructions'] == "Take medication daily"
        assert data['discharge_instructions_kinyarwanda'] == "Mfata umuti buri gihe"
        assert 'created_by_name' in data
        assert 'patient' in data
        assert 'hospital' in data
        assert 'length_of_stay_days' in data
        assert 'is_high_risk' in data


@pytest.mark.django_db
class TestDischargeSummaryCreateSerializer:
    """Test DischargeSummaryCreateSerializer."""
    
    def test_create_discharge_summary(self, rf):
        """Test creating discharge summary."""
        patient = PatientFactory()
        hospital = HospitalFactory()
        user = UserFactory()
        
        data = {
            'patient': patient.id,
            'hospital': hospital.id,
            'admission_date': date(2026, 1, 1),
            'discharge_date': date(2026, 1, 10),
            'primary_diagnosis': 'Hypertension',
            'treatment_summary': 'Medication and lifestyle changes',
            'discharge_condition': 'improved',
            'discharge_instructions': 'Take medication daily',
            'follow_up_required': True,
            'follow_up_timeframe': '1 week',
            'risk_level': 'medium',
            'attending_physician': 'Dr. Smith'
        }
        
        # Create a mock request
        request = rf.post('/api/discharge-summaries/')
        request.user = user
        
        serializer = DischargeSummaryCreateSerializer(
            data=data,
            context={'request': request}
        )
        assert serializer.is_valid()
        discharge = serializer.save()
        
        assert discharge.patient == patient
        assert discharge.hospital == hospital
        assert discharge.primary_diagnosis == 'Hypertension'
        assert discharge.created_by == user
    
    def test_validate_discharge_date_before_admission(self, rf):
        """Test validation fails when discharge date is before admission date."""
        patient = PatientFactory()
        hospital = HospitalFactory()
        
        data = {
            'patient': patient.id,
            'hospital': hospital.id,
            'admission_date': date(2026, 1, 10),
            'discharge_date': date(2026, 1, 5),
            'primary_diagnosis': 'Hypertension',
            'treatment_summary': 'Medication provided',
            'discharge_condition': 'improved',
            'discharge_instructions': 'Take medication',
            'risk_level': 'low',
            'attending_physician': 'Dr. Smith'
        }
        
        serializer = DischargeSummaryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'discharge_date' in serializer.errors
    
    def test_validate_follow_up_timeframe_required_when_follow_up(self, rf):
        """Test validation fails when follow_up_required but no timeframe."""
        patient = PatientFactory()
        hospital = HospitalFactory()
        
        data = {
            'patient': patient.id,
            'hospital': hospital.id,
            'admission_date': date(2026, 1, 1),
            'discharge_date': date(2026, 1, 10),
            'primary_diagnosis': 'Hypertension',
            'treatment_summary': 'Medication provided',
            'discharge_condition': 'improved',
            'discharge_instructions': 'Take medication',
            'follow_up_required': True,
            'risk_level': 'medium',
            'attending_physician': 'Dr. Smith'
        }
        
        serializer = DischargeSummaryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'follow_up_timeframe' in serializer.errors
