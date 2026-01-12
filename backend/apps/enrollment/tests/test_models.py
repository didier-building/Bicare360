"""
Unit tests for enrollment models (Hospital and DischargeSummary).
"""
import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.enrollment.models import Hospital, DischargeSummary
from apps.enrollment.tests.factories import HospitalFactory, DischargeSummaryFactory
from apps.patients.tests.factories import PatientFactory, UserFactory


@pytest.mark.django_db
class TestHospitalModel:
    """Test Hospital model."""
    
    def test_create_hospital_with_required_fields(self):
        """Test creating a hospital with all required fields."""
        hospital = HospitalFactory(
            name="Kigali University Teaching Hospital",
            code="CHUK",
            phone_number="+250788123456"
        )
        assert hospital.name == "Kigali University Teaching Hospital"
        assert hospital.code == "CHUK"
        assert hospital.phone_number == "+250788123456"
    
    def test_hospital_code_must_be_unique(self):
        """Test that hospital code must be unique."""
        HospitalFactory(code="CHUK")
        with pytest.raises(IntegrityError):
            HospitalFactory(code="CHUK")
    
    def test_hospital_phone_number_format(self):
        """Test that phone number must follow Rwanda format."""
        hospital = HospitalFactory.build(phone_number="invalid")
        with pytest.raises(ValidationError):
            hospital.full_clean()
    
    def test_hospital_phone_number_must_start_with_plus250(self):
        """Test that phone number must start with +250."""
        hospital = HospitalFactory.build(phone_number="+251788123456")
        with pytest.raises(ValidationError):
            hospital.full_clean()
    
    def test_hospital_str_representation(self):
        """Test string representation of hospital."""
        hospital = HospitalFactory(name="Kigali Hospital", code="KH01")
        assert str(hospital) == "Kigali Hospital (KH01)"
    
    def test_hospital_ordering_by_name(self):
        """Test that hospitals are ordered by name."""
        HospitalFactory(name="Zebra Hospital")
        HospitalFactory(name="Alpha Hospital")
        hospitals = Hospital.objects.all()
        assert hospitals[0].name == "Alpha Hospital"
        assert hospitals[1].name == "Zebra Hospital"
    
    def test_hospital_types(self):
        """Test all hospital type choices."""
        types = ["referral", "district", "health_center", "clinic"]
        for hospital_type in types:
            hospital = HospitalFactory(hospital_type=hospital_type)
            assert hospital.hospital_type == hospital_type
    
    def test_hospital_status_choices(self):
        """Test all status choices."""
        statuses = ["active", "pilot", "inactive"]
        for status in statuses:
            hospital = HospitalFactory(status=status)
            assert hospital.status == status
    
    def test_hospital_emr_integration_types(self):
        """Test EMR integration type choices."""
        types = ["manual", "api", "hl7"]
        for emr_type in types:
            hospital = HospitalFactory(emr_integration_type=emr_type)
            assert hospital.emr_integration_type == emr_type
    
    def test_hospital_timestamps(self):
        """Test that timestamps are auto-generated."""
        hospital = HospitalFactory()
        assert hospital.created_at is not None
        assert hospital.updated_at is not None


@pytest.mark.django_db
class TestDischargeSummaryModel:
    """Test DischargeSummary model."""
    
    def test_create_discharge_summary_with_required_fields(self):
        """Test creating discharge summary with required fields."""
        patient = PatientFactory()
        hospital = HospitalFactory()
        user = UserFactory()
        
        discharge = DischargeSummaryFactory(
            patient=patient,
            hospital=hospital,
            admission_date=date(2026, 1, 1),
            discharge_date=date(2026, 1, 10),
            primary_diagnosis="Hypertension",
            treatment_summary="Medication and lifestyle changes",
            discharge_instructions="Take medication daily",
            attending_physician="Dr. Smith",
            created_by=user
        )
        
        assert discharge.patient == patient
        assert discharge.hospital == hospital
        assert discharge.primary_diagnosis == "Hypertension"
    
    def test_length_of_stay_calculated_automatically(self):
        """Test that length of stay is calculated on save."""
        discharge = DischargeSummaryFactory(
            admission_date=date(2026, 1, 1),
            discharge_date=date(2026, 1, 10)
        )
        assert discharge.length_of_stay_days == 9
    
    def test_length_of_stay_for_same_day_discharge(self):
        """Test length of stay for same-day discharge."""
        discharge = DischargeSummaryFactory(
            admission_date=date(2026, 1, 1),
            discharge_date=date(2026, 1, 1)
        )
        assert discharge.length_of_stay_days == 0
    
    def test_length_of_stay_recalculated_on_update(self):
        """Test that length of stay is recalculated when dates change."""
        discharge = DischargeSummaryFactory(
            admission_date=date(2026, 1, 1),
            discharge_date=date(2026, 1, 5)
        )
        assert discharge.length_of_stay_days == 4
        
        discharge.discharge_date = date(2026, 1, 10)
        discharge.save()
        assert discharge.length_of_stay_days == 9
    
    def test_is_high_risk_property_for_high_risk(self):
        """Test is_high_risk property returns True for high risk."""
        discharge = DischargeSummaryFactory(risk_level="high")
        assert discharge.is_high_risk is True
    
    def test_is_high_risk_property_for_critical(self):
        """Test is_high_risk property returns True for critical."""
        discharge = DischargeSummaryFactory(risk_level="critical")
        assert discharge.is_high_risk is True
    
    def test_is_high_risk_property_for_medium_risk(self):
        """Test is_high_risk property returns False for medium risk."""
        discharge = DischargeSummaryFactory(risk_level="medium")
        assert discharge.is_high_risk is False
    
    def test_is_high_risk_property_for_low_risk(self):
        """Test is_high_risk property returns False for low risk."""
        discharge = DischargeSummaryFactory(risk_level="low")
        assert discharge.is_high_risk is False
    
    def test_days_since_discharge_property(self):
        """Test days_since_discharge calculation."""
        discharge = DischargeSummaryFactory(
            admission_date=date.today() - timedelta(days=10),
            discharge_date=date.today() - timedelta(days=5)
        )
        assert discharge.days_since_discharge == 5
    
    def test_days_since_discharge_for_today(self):
        """Test days_since_discharge for today's discharge."""
        discharge = DischargeSummaryFactory(discharge_date=date.today())
        assert discharge.days_since_discharge == 0
    
    def test_discharge_summary_str_representation(self):
        """Test string representation."""
        patient = PatientFactory(first_name="John", last_name="Doe")
        hospital = HospitalFactory(code="CHUK")
        discharge = DischargeSummaryFactory(
            patient=patient,
            hospital=hospital,
            discharge_date=date(2026, 1, 10)
        )
        assert "John Doe" in str(discharge)
        assert "CHUK" in str(discharge)
        assert "2026-01-10" in str(discharge)
    
    def test_discharge_summary_ordering(self):
        """Test that discharge summaries are ordered by discharge date desc."""
        DischargeSummaryFactory(
            admission_date=date(2025, 12, 28),
            discharge_date=date(2026, 1, 1)
        )
        DischargeSummaryFactory(
            admission_date=date(2026, 1, 10),
            discharge_date=date(2026, 1, 15)
        )
        DischargeSummaryFactory(
            admission_date=date(2026, 1, 5),
            discharge_date=date(2026, 1, 10)
        )
        
        summaries = DischargeSummary.objects.all()
        assert summaries[0].discharge_date == date(2026, 1, 15)
        assert summaries[1].discharge_date == date(2026, 1, 10)
        assert summaries[2].discharge_date == date(2026, 1, 1)
    
    def test_patient_can_have_multiple_discharge_summaries(self):
        """Test that a patient can have multiple discharge summaries."""
        patient = PatientFactory()
        DischargeSummaryFactory.create_batch(3, patient=patient)
        assert patient.discharge_summaries.count() == 3
    
    def test_discharge_summary_cascade_delete_with_patient(self):
        """Test that discharge summaries are deleted when patient is deleted."""
        patient = PatientFactory()
        DischargeSummaryFactory.create_batch(2, patient=patient)
        patient.delete()
        assert DischargeSummary.objects.filter(patient=patient).count() == 0
    
    def test_discharge_summary_protected_from_hospital_delete(self):
        """Test that hospital cannot be deleted if it has discharge summaries."""
        hospital = HospitalFactory()
        DischargeSummaryFactory(hospital=hospital)
        with pytest.raises(Exception):  # Django ProtectedError
            hospital.delete()
    
    def test_discharge_condition_choices(self):
        """Test all discharge condition choices."""
        conditions = ["improved", "stable", "unchanged", "deteriorated"]
        for condition in conditions:
            discharge = DischargeSummaryFactory(discharge_condition=condition)
            assert discharge.discharge_condition == condition
    
    def test_risk_level_choices(self):
        """Test all risk level choices."""
        levels = ["low", "medium", "high", "critical"]
        for level in levels:
            discharge = DischargeSummaryFactory(risk_level=level)
            assert discharge.risk_level == level
    
    def test_follow_up_not_required(self):
        """Test discharge with follow_up_required=False."""
        discharge = DischargeSummaryFactory(follow_up_required=False)
        assert discharge.follow_up_required is False
    
    def test_discharge_with_kinyarwanda_instructions(self):
        """Test discharge with Kinyarwanda instructions."""
        discharge = DischargeSummaryFactory(
            discharge_instructions_kinyarwanda="Mfata umuti wawe buri gihe"
        )
        assert discharge.discharge_instructions_kinyarwanda == "Mfata umuti wawe buri gihe"
    
    def test_discharge_with_icd10_codes(self):
        """Test discharge with ICD-10 codes."""
        discharge = DischargeSummaryFactory(
            icd10_primary="I10",
            icd10_secondary="E11, J44.9"
        )
        assert discharge.icd10_primary == "I10"
        assert discharge.icd10_secondary == "E11, J44.9"
    
    def test_discharge_timestamps(self):
        """Test that timestamps are auto-generated."""
        discharge = DischargeSummaryFactory()
        assert discharge.created_at is not None
        assert discharge.updated_at is not None
