import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta, time
from apps.medications.models import Medication, Prescription, MedicationAdherence
from apps.patients.tests.factories import PatientFactory
from apps.enrollment.tests.factories import DischargeSummaryFactory, HospitalFactory


@pytest.mark.django_db
class TestMedicationModel:
    """Test suite for Medication model"""
    
    def test_create_medication_with_all_fields(self):
        """Test creating a medication with all fields"""
        medication = Medication.objects.create(
            name='Paracetamol 500mg Tablets',
            generic_name='Paracetamol',
            brand_name='Panadol',
            dosage_form='tablet',
            strength='500mg',
            manufacturer='GSK',
            description='Pain reliever and fever reducer',
            indication='For relief of mild to moderate pain and fever',
            contraindications='Severe liver disease',
            side_effects='Nausea, rash, liver damage (rare)',
            storage_instructions='Store at room temperature',
            requires_prescription=True,
            is_active=True
        )
        
        assert medication.id is not None
        assert medication.name == 'Paracetamol 500mg Tablets'
        assert medication.generic_name == 'Paracetamol'
        assert medication.brand_name == 'Panadol'
        assert medication.dosage_form == 'tablet'
        assert medication.strength == '500mg'
        assert medication.manufacturer == 'GSK'
        assert medication.requires_prescription is True
        assert medication.is_active is True
        assert medication.created_at is not None
        assert medication.updated_at is not None
    
    def test_create_medication_with_required_fields_only(self):
        """Test creating medication with only required fields"""
        medication = Medication.objects.create(
            name='Aspirin',
            generic_name='Acetylsalicylic acid',
            dosage_form='tablet',
            strength='100mg'
        )
        
        assert medication.id is not None
        assert medication.name == 'Aspirin'
        assert medication.generic_name == 'Acetylsalicylic acid'
        assert medication.brand_name is None
        assert medication.requires_prescription is False  # Default
        assert medication.is_active is True  # Default
    
    def test_medication_name_required(self):
        """Test that medication name is required"""
        with pytest.raises(ValidationError):
            medication = Medication(
                generic_name='Test',
                dosage_form='tablet',
                strength='100mg'
            )
            medication.full_clean()
    
    def test_medication_generic_name_required(self):
        """Test that generic name is required"""
        with pytest.raises(ValidationError):
            medication = Medication(
                name='Test Medicine',
                dosage_form='tablet',
                strength='100mg'
            )
            medication.full_clean()
    
    def test_medication_dosage_form_required(self):
        """Test that dosage form is required"""
        with pytest.raises(ValidationError):
            medication = Medication(
                name='Test Medicine',
                generic_name='Test',
                strength='100mg'
            )
            medication.full_clean()
    
    def test_medication_dosage_form_choices(self):
        """Test that only valid dosage form choices are accepted"""
        valid_forms = ['tablet', 'capsule', 'syrup', 'injection', 'cream', 'ointment', 'drops', 'inhaler', 'patch', 'suppository']
        
        for form in valid_forms:
            medication = Medication(
                name=f'Test {form}',
                generic_name='Test',
                dosage_form=form,
                strength='100mg'
            )
            medication.full_clean()  # Should not raise
        
        # Test invalid form
        with pytest.raises(ValidationError):
            medication = Medication(
                name='Test',
                generic_name='Test',
                dosage_form='invalid_form',
                strength='100mg'
            )
            medication.full_clean()
    
    def test_medication_strength_required(self):
        """Test that strength is required"""
        with pytest.raises(ValidationError):
            medication = Medication(
                name='Test Medicine',
                generic_name='Test',
                dosage_form='tablet'
            )
            medication.full_clean()
    
    def test_medication_str_method(self):
        """Test the string representation of medication"""
        medication = Medication.objects.create(
            name='Ibuprofen 400mg',
            generic_name='Ibuprofen',
            dosage_form='tablet',
            strength='400mg'
        )
        
        assert str(medication) == 'Ibuprofen 400mg (400mg)'
    
    def test_medication_ordering(self):
        """Test that medications are ordered by name"""
        Medication.objects.create(
            name='Zinc Tablets',
            generic_name='Zinc',
            dosage_form='tablet',
            strength='50mg'
        )
        Medication.objects.create(
            name='Aspirin',
            generic_name='Acetylsalicylic acid',
            dosage_form='tablet',
            strength='100mg'
        )
        Medication.objects.create(
            name='Multivitamin',
            generic_name='Multivitamin',
            dosage_form='tablet',
            strength='1 tablet'
        )
        
        medications = list(Medication.objects.all())
        assert medications[0].name == 'Aspirin'
        assert medications[1].name == 'Multivitamin'
        assert medications[2].name == 'Zinc Tablets'
    
    def test_medication_is_active_default_true(self):
        """Test that is_active defaults to True"""
        medication = Medication.objects.create(
            name='Test',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        
        assert medication.is_active is True
    
    def test_medication_requires_prescription_default_false(self):
        """Test that requires_prescription defaults to False"""
        medication = Medication.objects.create(
            name='Test',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        
        assert medication.requires_prescription is False
    
    def test_medication_timestamps(self):
        """Test that timestamps are automatically set"""
        from datetime import timedelta
        
        medication = Medication.objects.create(
            name='Test',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        
        assert medication.created_at is not None
        assert medication.updated_at is not None
        # Check timestamps are within 1 second of each other
        assert abs((medication.created_at - medication.updated_at).total_seconds()) < 1
        
        # Update and check updated_at changes
        original_updated = medication.updated_at
        medication.description = 'Updated description'
        medication.save()
        
        assert medication.updated_at > original_updated
    
    def test_filter_active_medications(self):
        """Test filtering active medications"""
        Medication.objects.create(
            name='Active Med',
            generic_name='Active',
            dosage_form='tablet',
            strength='100mg',
            is_active=True
        )
        Medication.objects.create(
            name='Inactive Med',
            generic_name='Inactive',
            dosage_form='tablet',
            strength='100mg',
            is_active=False
        )
        
        active_meds = Medication.objects.filter(is_active=True)
        assert active_meds.count() == 1
        assert active_meds.first().name == 'Active Med'
    
    def test_filter_by_dosage_form(self):
        """Test filtering by dosage form"""
        Medication.objects.create(
            name='Tablet Med',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        Medication.objects.create(
            name='Syrup Med',
            generic_name='Test',
            dosage_form='syrup',
            strength='5ml'
        )
        
        tablets = Medication.objects.filter(dosage_form='tablet')
        assert tablets.count() == 1
        assert tablets.first().name == 'Tablet Med'
    
    def test_search_by_name_or_generic_name(self):
        """Test searching medications by name or generic name"""
        Medication.objects.create(
            name='Panadol',
            generic_name='Paracetamol',
            dosage_form='tablet',
            strength='500mg'
        )
        Medication.objects.create(
            name='Ibuprofen Tablets',
            generic_name='Ibuprofen',
            dosage_form='tablet',
            strength='400mg'
        )
        
        # Search by brand name
        results = Medication.objects.filter(name__icontains='panadol')
        assert results.count() == 1
        
        # Search by generic name
        results = Medication.objects.filter(generic_name__icontains='paracetamol')
        assert results.count() == 1
    
    def test_medication_name_max_length(self):
        """Test that name has max length of 200"""
        long_name = 'A' * 201
        with pytest.raises(ValidationError):
            medication = Medication(
                name=long_name,
                generic_name='Test',
                dosage_form='tablet',
                strength='100mg'
            )
            medication.full_clean()
    
    def test_medication_verbose_name_plural(self):
        """Test the verbose name plural"""
        assert Medication._meta.verbose_name_plural == 'medications'


@pytest.mark.django_db
class TestPrescriptionModel:
    """Test suite for Prescription model"""
    
    def test_create_prescription_with_all_fields(self):
        """Test creating a prescription with all fields"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Amoxicillin 500mg',
            generic_name='Amoxicillin',
            dosage_form='capsule',
            strength='500mg'
        )
        hospital = HospitalFactory()
        discharge_summary = DischargeSummaryFactory(patient=patient, hospital=hospital)
        
        prescription = Prescription.objects.create(
            discharge_summary=discharge_summary,
            patient=patient,
            medication=medication,
            dosage='500mg',
            frequency='3 times daily',
            frequency_times_per_day=3,
            route='oral',
            duration_days=7,
            quantity=21,
            instructions='Take with food',
            instructions_kinyarwanda='Urye hamwe nibiryo',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=7),
            prescribed_by='Dr. Smith',
            refills_allowed=0,
            is_active=True
        )
        
        assert prescription.id is not None
        assert prescription.patient == patient
        assert prescription.medication == medication
        assert prescription.discharge_summary == discharge_summary
        assert prescription.dosage == '500mg'
        assert prescription.frequency == '3 times daily'
        assert prescription.frequency_times_per_day == 3
        assert prescription.route == 'oral'
        assert prescription.duration_days == 7
        assert prescription.quantity == 21
        assert prescription.is_active is True
    
    def test_create_prescription_with_required_fields_only(self):
        """Test creating prescription with only required fields"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Paracetamol',
            generic_name='Paracetamol',
            dosage_form='tablet',
            strength='500mg'
        )
        
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='500mg',
            frequency='twice daily',
            frequency_times_per_day=2,
            duration_days=5
        )
        
        assert prescription.id is not None
        assert prescription.discharge_summary is None
        assert prescription.route == 'oral'  # Default
        assert prescription.is_active is True  # Default
    
    def test_prescription_patient_required(self):
        """Test that patient is required"""
        medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        
        with pytest.raises(IntegrityError):
            Prescription.objects.create(
                medication=medication,
                dosage='100mg',
                frequency='once daily',
                frequency_times_per_day=1,
                duration_days=5
            )
    
    def test_prescription_medication_required(self):
        """Test that medication is required"""
        patient = PatientFactory()
        
        with pytest.raises(IntegrityError):
            Prescription.objects.create(
                patient=patient,
                dosage='100mg',
                frequency='once daily',
                frequency_times_per_day=1,
                duration_days=5
            )
    
    def test_prescription_dosage_required(self):
        """Test that dosage is required"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        
        with pytest.raises(ValidationError):
            prescription = Prescription(
                patient=patient,
                medication=medication,
                frequency='once daily',
                frequency_times_per_day=1,
                duration_days=5
            )
            prescription.full_clean()
    
    def test_prescription_frequency_required(self):
        """Test that frequency is required"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test',
            dosage_form='tablet',
            strength='100mg'
        )
        
        with pytest.raises(ValidationError):
            prescription = Prescription(
                patient=patient,
                medication=medication,
                dosage='100mg',
                frequency_times_per_day=1,
                duration_days=5
            )
            prescription.full_clean()
    
    def test_prescription_route_choices(self):
        """Test that only valid route choices are accepted"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med',
            generic_name='Test',
            dosage_form='injection',
            strength='10mg/ml'
        )
        
        valid_routes = ['oral', 'topical', 'intravenous', 'intramuscular', 'subcutaneous', 'inhalation', 'rectal', 'transdermal']
        
        for route in valid_routes:
            prescription = Prescription(
                patient=patient,
                medication=medication,
                dosage='10mg',
                frequency='once daily',
                frequency_times_per_day=1,
                route=route,
                duration_days=5
            )
            prescription.full_clean()  # Should not raise
        
        # Test invalid route
        with pytest.raises(ValidationError):
            prescription = Prescription(
                patient=patient,
                medication=medication,
                dosage='10mg',
                frequency='once daily',
                frequency_times_per_day=1,
                route='invalid_route',
                duration_days=5
            )
            prescription.full_clean()
    
    def test_prescription_str_method(self):
        """Test the string representation of prescription"""
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
        
        expected = f'{patient.full_name} - Amoxicillin 500mg (500mg, 3 times daily)'
        assert str(prescription) == expected
    
    def test_prescription_ordering(self):
        """Test that prescriptions are ordered by created_at descending"""
        patient = PatientFactory()
        med1 = Medication.objects.create(name='Med1', generic_name='Med1', dosage_form='tablet', strength='100mg')
        med2 = Medication.objects.create(name='Med2', generic_name='Med2', dosage_form='tablet', strength='200mg')
        med3 = Medication.objects.create(name='Med3', generic_name='Med3', dosage_form='tablet', strength='300mg')
        
        p1 = Prescription.objects.create(
            patient=patient, medication=med1, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        p2 = Prescription.objects.create(
            patient=patient, medication=med2, dosage='200mg',
            frequency='twice', frequency_times_per_day=2, duration_days=5
        )
        p3 = Prescription.objects.create(
            patient=patient, medication=med3, dosage='300mg',
            frequency='thrice', frequency_times_per_day=3, duration_days=5
        )
        
        prescriptions = list(Prescription.objects.all())
        # Should be ordered by created_at descending (newest first)
        assert prescriptions[0].id == p3.id
        assert prescriptions[1].id == p2.id
        assert prescriptions[2].id == p1.id
    
    def test_prescription_is_active_default_true(self):
        """Test that is_active defaults to True"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=5
        )
        
        assert prescription.is_active is True
    
    def test_prescription_route_default_oral(self):
        """Test that route defaults to oral"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=5
        )
        
        assert prescription.route == 'oral'
    
    def test_prescription_timestamps(self):
        """Test that timestamps are automatically set"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=5
        )
        
        assert prescription.created_at is not None
        assert prescription.updated_at is not None
    
    def test_prescription_is_current_property(self):
        """Test the is_current computed property"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        # Current prescription (active and within date range)
        today = timezone.now().date()
        current_prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=5),
            is_active=True
        )
        
        assert current_prescription.is_current is True
        
        # Expired prescription
        expired_prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7,
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=3),
            is_active=True
        )
        
        assert expired_prescription.is_current is False
        
        # Inactive prescription
        inactive_prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7,
            start_date=today,
            end_date=today + timedelta(days=7),
            is_active=False
        )
        
        assert inactive_prescription.is_current is False
    
    def test_prescription_days_remaining_property(self):
        """Test the days_remaining computed property"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        today = timezone.now().date()
        
        # Prescription with days remaining
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7,
            start_date=today,
            end_date=today + timedelta(days=5)
        )
        
        assert prescription.days_remaining == 5
        
        # Expired prescription
        expired = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7,
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=3)
        )
        
        assert expired.days_remaining == 0
        
        # Prescription without end date
        no_end_date = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage='100mg',
            frequency='once daily',
            frequency_times_per_day=1,
            duration_days=7
        )
        
        assert no_end_date.days_remaining is None
    
    def test_filter_active_prescriptions(self):
        """Test filtering active prescriptions"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5, is_active=True
        )
        Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5, is_active=False
        )
        
        active = Prescription.objects.filter(is_active=True)
        assert active.count() == 1
    
    def test_filter_by_patient(self):
        """Test filtering prescriptions by patient"""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        Prescription.objects.create(
            patient=patient1, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        Prescription.objects.create(
            patient=patient2, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        patient1_prescriptions = Prescription.objects.filter(patient=patient1)
        assert patient1_prescriptions.count() == 1
    
    def test_filter_by_medication(self):
        """Test filtering prescriptions by medication"""
        patient = PatientFactory()
        med1 = Medication.objects.create(name='Med1', generic_name='Med1', dosage_form='tablet', strength='100mg')
        med2 = Medication.objects.create(name='Med2', generic_name='Med2', dosage_form='tablet', strength='200mg')
        
        Prescription.objects.create(
            patient=patient, medication=med1, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        Prescription.objects.create(
            patient=patient, medication=med2, dosage='200mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        med1_prescriptions = Prescription.objects.filter(medication=med1)
        assert med1_prescriptions.count() == 1
    
    def test_prescription_cascade_delete_patient(self):
        """Test that prescriptions are deleted when patient is deleted"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        assert Prescription.objects.count() == 1
        patient.delete()
        assert Prescription.objects.count() == 0
    
    def test_prescription_protect_medication(self):
        """Test that medication cannot be deleted if prescriptions exist"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        from django.db.models import ProtectedError
        with pytest.raises(ProtectedError):
            medication.delete()
    
    def test_prescription_duration_positive(self):
        """Test that duration_days must be positive"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        with pytest.raises(ValidationError):
            prescription = Prescription(
                patient=patient,
                medication=medication,
                dosage='100mg',
                frequency='once daily',
                frequency_times_per_day=1,
                duration_days=-5
            )
            prescription.full_clean()
    
    def test_prescription_frequency_times_positive(self):
        """Test that frequency_times_per_day must be positive"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        
        with pytest.raises(ValidationError):
            prescription = Prescription(
                patient=patient,
                medication=medication,
                dosage='100mg',
                frequency='once daily',
                frequency_times_per_day=0,
                duration_days=5
            )
            prescription.full_clean()


@pytest.mark.django_db
class TestMedicationAdherenceModel:
    """Test suite for MedicationAdherence model"""
    
    def test_create_adherence_record_taken(self):
        """Test creating an adherence record when medication is taken"""
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
            frequency='twice daily',
            frequency_times_per_day=2,
            duration_days=7
        )
        
        adherence = MedicationAdherence.objects.create(
            prescription=prescription,
            patient=patient,
            scheduled_time=time(9, 0),  # 9:00 AM
            status='taken',
            taken_at=timezone.now(),
            notes='Taken with breakfast'
        )
        
        assert adherence.id is not None
        assert adherence.prescription == prescription
        assert adherence.patient == patient
        assert adherence.status == 'taken'
        assert adherence.scheduled_time == time(9, 0)
        assert adherence.taken_at is not None
        assert adherence.notes == 'Taken with breakfast'
    
    def test_create_adherence_record_missed(self):
        """Test creating an adherence record when medication is missed"""
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
            status='missed',
            reason_missed='Forgot to take it'
        )
        
        assert adherence.status == 'missed'
        assert adherence.taken_at is None
        assert adherence.reason_missed == 'Forgot to take it'
    
    def test_create_adherence_record_skipped(self):
        """Test creating an adherence record when medication is skipped"""
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
            scheduled_time=time(20, 0),
            status='skipped',
            reason_missed='Felt nauseous'
        )
        
        assert adherence.status == 'skipped'
        assert adherence.reason_missed == 'Felt nauseous'
    
    def test_adherence_prescription_required(self):
        """Test that prescription is required"""
        patient = PatientFactory()
        
        with pytest.raises(IntegrityError):
            MedicationAdherence.objects.create(
                patient=patient,
                scheduled_time=time(8, 0),
                status='taken'
            )
    
    def test_adherence_patient_required(self):
        """Test that patient is required"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        with pytest.raises(IntegrityError):
            MedicationAdherence.objects.create(
                prescription=prescription,
                scheduled_time=time(8, 0),
                status='taken'
            )
    
    def test_adherence_scheduled_time_required(self):
        """Test that scheduled_time is required"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        with pytest.raises(ValidationError):
            adherence = MedicationAdherence(
                prescription=prescription,
                patient=patient,
                status='taken'
            )
            adherence.full_clean()
    
    def test_adherence_status_required(self):
        """Test that status has a default value"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        # Status has default value of 'scheduled'
        adherence = MedicationAdherence(
            prescription=prescription,
            patient=patient,
            scheduled_time=time(8, 0)
        )
        adherence.full_clean()
        assert adherence.status == 'scheduled'
    
    def test_adherence_status_choices(self):
        """Test that only valid status choices are accepted"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        valid_statuses = ['scheduled', 'taken', 'missed', 'skipped', 'late']
        
        for status in valid_statuses:
            adherence = MedicationAdherence(
                prescription=prescription,
                patient=patient,
                scheduled_time=time(8, 0),
                status=status
            )
            adherence.full_clean()  # Should not raise
        
        # Test invalid status
        with pytest.raises(ValidationError):
            adherence = MedicationAdherence(
                prescription=prescription,
                patient=patient,
                scheduled_time=time(8, 0),
                status='invalid_status'
            )
            adherence.full_clean()
    
    def test_adherence_str_method(self):
        """Test the string representation of adherence record"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Amoxicillin',
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
        
        adherence = MedicationAdherence.objects.create(
            prescription=prescription,
            patient=patient,
            scheduled_date=timezone.now().date(),
            scheduled_time=time(9, 0),
            status='taken'
        )
        
        expected = f'{patient.full_name} - Amoxicillin - {adherence.scheduled_date} 09:00:00 (taken)'
        assert str(adherence) == expected
    
    def test_adherence_ordering(self):
        """Test that adherence records are ordered by scheduled_date and time descending"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='3 times', frequency_times_per_day=3, duration_days=5
        )
        
        today = timezone.now().date()
        
        a1 = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=today, scheduled_time=time(8, 0), status='taken'
        )
        a2 = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=today, scheduled_time=time(14, 0), status='taken'
        )
        a3 = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=today, scheduled_time=time(20, 0), status='scheduled'
        )
        
        adherences = list(MedicationAdherence.objects.all())
        # Should be ordered by date and time descending
        assert adherences[0].id == a3.id
        assert adherences[1].id == a2.id
        assert adherences[2].id == a1.id
    
    def test_adherence_timestamps(self):
        """Test that timestamps are automatically set"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        adherence = MedicationAdherence.objects.create(
            prescription=prescription,
            patient=patient,
            scheduled_time=time(8, 0),
            status='taken'
        )
        
        assert adherence.created_at is not None
        assert adherence.updated_at is not None
    
    def test_adherence_is_late_property(self):
        """Test the is_late computed property"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        # Taken on time
        on_time = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0),
            taken_at=timezone.make_aware(timezone.datetime.combine(timezone.now().date(), time(8, 15))),
            status='taken'
        )
        assert on_time.is_overdue is False
        
        # Taken late (more than 30 minutes)
        late = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(14, 0),
            taken_at=timezone.make_aware(timezone.datetime.combine(timezone.now().date(), time(15, 0))),
            status='late'
        )
        assert late.is_overdue is False  # Already taken, not overdue
        
        # Not taken yet - scheduled in future (tomorrow at 10 AM)
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        scheduled = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=tomorrow,
            scheduled_time=time(10, 0),
            status='scheduled'
        )
        assert scheduled.is_overdue is False
    
    def test_adherence_minutes_late_property(self):
        """Test the minutes_late computed property"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        # Taken 45 minutes late
        today = timezone.now().date()
        scheduled_dt = timezone.make_aware(timezone.datetime.combine(today, time(8, 0)))
        taken_dt = timezone.make_aware(timezone.datetime.combine(today, time(8, 45)))
        adherence = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=today,
            scheduled_time=time(8, 0),
            taken_at=taken_dt,
            status='late'
        )
        assert adherence.minutes_late == 45
        
        # Taken early (negative minutes late)
        scheduled_dt2 = timezone.make_aware(timezone.datetime.combine(today, time(14, 0)))
        taken_dt2 = timezone.make_aware(timezone.datetime.combine(today, time(13, 50)))
        early = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=today,
            scheduled_time=time(14, 0),
            taken_at=taken_dt2,
            status='late'  # Still marked as late since logic requires this status
        )
        assert early.minutes_late == -10
        
        # No taken_at
        no_actual = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(20, 0),
            status='scheduled'
        )
        assert no_actual.minutes_late is None
    
    def test_filter_by_status(self):
        """Test filtering adherence records by status"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='3 times', frequency_times_per_day=3, duration_days=5
        )
        
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='taken'
        )
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(14, 0), status='missed'
        )
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(20, 0), status='scheduled'
        )
        
        taken = MedicationAdherence.objects.filter(status='taken')
        missed = MedicationAdherence.objects.filter(status='missed')
        
        assert taken.count() == 1
        assert missed.count() == 1
    
    def test_filter_by_patient(self):
        """Test filtering adherence records by patient"""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        p1 = Prescription.objects.create(
            patient=patient1, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        p2 = Prescription.objects.create(
            patient=patient2, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        MedicationAdherence.objects.create(
            prescription=p1, patient=patient1,
            scheduled_time=time(8, 0), status='taken'
        )
        MedicationAdherence.objects.create(
            prescription=p2, patient=patient2,
            scheduled_time=time(8, 0), status='taken'
        )
        
        patient1_adherence = MedicationAdherence.objects.filter(patient=patient1)
        assert patient1_adherence.count() == 1
    
    def test_filter_by_prescription(self):
        """Test filtering adherence records by prescription"""
        patient = PatientFactory()
        med1 = Medication.objects.create(name='Med1', generic_name='Med1', dosage_form='tablet', strength='100mg')
        med2 = Medication.objects.create(name='Med2', generic_name='Med2', dosage_form='tablet', strength='200mg')
        
        p1 = Prescription.objects.create(
            patient=patient, medication=med1, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        p2 = Prescription.objects.create(
            patient=patient, medication=med2, dosage='200mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        MedicationAdherence.objects.create(
            prescription=p1, patient=patient,
            scheduled_time=time(8, 0), status='taken'
        )
        MedicationAdherence.objects.create(
            prescription=p2, patient=patient,
            scheduled_time=time(8, 0), status='taken'
        )
        
        p1_adherence = MedicationAdherence.objects.filter(prescription=p1)
        assert p1_adherence.count() == 1
    
    def test_filter_by_date_range(self):
        """Test filtering adherence records by date range"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=yesterday, scheduled_time=time(8, 0), status='taken'
        )
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=today, scheduled_time=time(8, 0), status='taken'
        )
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=tomorrow, scheduled_time=time(8, 0), status='scheduled'
        )
        
        today_records = MedicationAdherence.objects.filter(scheduled_date=today)
        assert today_records.count() == 1
    
    def test_adherence_cascade_delete_prescription(self):
        """Test that adherence records are deleted when prescription is deleted"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='taken'
        )
        
        assert MedicationAdherence.objects.count() == 1
        prescription.delete()
        assert MedicationAdherence.objects.count() == 0
    
    def test_adherence_cascade_delete_patient(self):
        """Test that adherence records are deleted when patient is deleted"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='taken'
        )
        
        assert MedicationAdherence.objects.count() == 1
        patient.delete()
        assert MedicationAdherence.objects.count() == 0
    
    def test_scheduled_date_default_today(self):
        """Test that scheduled_date defaults to today if not specified"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test', generic_name='Test', dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication, dosage='100mg',
            frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        today = timezone.now().date()
        adherence = MedicationAdherence.objects.create(
            prescription=prescription,
            patient=patient,
            scheduled_time=time(8, 0),
            status='taken'
        )
        
        # scheduled_date should be a date object, not datetime
        from datetime import date
        assert isinstance(adherence.scheduled_date, date)
        assert adherence.scheduled_date == today
