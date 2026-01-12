"""
Tests for Patient models.
Following TDD: These tests were written first, then models implemented.
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from apps.patients.models import Patient, Address, EmergencyContact
from apps.patients.tests.factories import (
    PatientFactory,
    AddressFactory,
    EmergencyContactFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestPatientModel:
    """Test suite for Patient model."""

    def test_create_patient_with_required_fields(self):
        """Test creating a patient with all required fields."""
        user = UserFactory()
        patient = PatientFactory(enrolled_by=user)

        assert patient.id is not None
        assert patient.first_name
        assert patient.last_name
        assert patient.national_id
        assert patient.phone_number
        assert patient.date_of_birth
        assert patient.gender in ["M", "F", "O"]
        assert patient.is_active is True

    def test_patient_national_id_must_be_16_digits(self):
        """Test that national ID must be exactly 16 digits."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(national_id="12345")  # Too short
            patient.full_clean()

    def test_patient_national_id_must_be_unique(self):
        """Test that national ID must be unique across patients."""
        national_id = "1234567890123456"
        PatientFactory(national_id=national_id)

        with pytest.raises(IntegrityError):
            PatientFactory(national_id=national_id)

    def test_patient_phone_number_format(self):
        """Test phone number validation."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(phone_number="123456789")  # Invalid format
            patient.full_clean()

    def test_patient_phone_number_must_start_with_plus250(self):
        """Test that phone numbers must start with +250."""
        patient = PatientFactory(phone_number="+250788123456")
        assert patient.phone_number.startswith("+250")

    def test_patient_full_name_property(self):
        """Test the full_name property."""
        patient = PatientFactory(first_name="John", last_name="Doe")
        assert patient.full_name == "John Doe"

    def test_patient_age_calculation(self):
        """Test age calculation from date of birth."""
        # Patient born 25 years ago
        birth_date = date.today() - timedelta(days=365 * 25 + 6)  # +6 for leap years
        patient = PatientFactory(date_of_birth=birth_date)

        assert 24 <= patient.age <= 25  # Account for timing differences

    def test_patient_str_representation(self):
        """Test string representation of patient."""
        patient = PatientFactory(
            first_name="John",
            last_name="Doe",
            national_id="1234567890123456",
        )
        assert "John Doe" in str(patient)
        assert "1234567890123456" in str(patient)

    def test_patient_ordering_by_enrolled_date_desc(self):
        """Test that patients are ordered by enrollment date descending."""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        patient3 = PatientFactory()

        patients = Patient.objects.all()
        assert patients[0] == patient3  # Most recent
        assert patients[2] == patient1  # Oldest

    def test_patient_can_have_kinyarwanda_name(self):
        """Test that patients can have Kinyarwanda names."""
        patient = PatientFactory(
            first_name="John",
            last_name="Doe",
            first_name_kinyarwanda="Yohani",
            last_name_kinyarwanda="Umuhigi",
        )
        assert patient.first_name_kinyarwanda == "Yohani"
        assert patient.last_name_kinyarwanda == "Umuhigi"

    def test_patient_language_preference_default_kinyarwanda(self):
        """Test that default language preference is Kinyarwanda."""
        patient = PatientFactory()
        assert patient.language_preference == "kin"

    def test_patient_prefers_sms_by_default(self):
        """Test that SMS is preferred by default."""
        patient = PatientFactory()
        assert patient.prefers_sms is True
        assert patient.prefers_whatsapp is False


@pytest.mark.django_db
class TestAddressModel:
    """Test suite for Address model."""

    def test_create_address_for_patient(self):
        """Test creating an address for a patient."""
        patient = PatientFactory()
        address = AddressFactory(patient=patient)

        assert address.id is not None
        assert address.patient == patient
        assert address.province
        assert address.district
        assert address.sector
        assert address.cell
        assert address.village

    def test_address_one_to_one_with_patient(self):
        """Test that each patient can have only one address."""
        patient = PatientFactory()
        AddressFactory(patient=patient)

        # Attempting to create another address should fail
        with pytest.raises(IntegrityError):
            AddressFactory(patient=patient)

    def test_address_cascade_delete_with_patient(self):
        """Test that address is deleted when patient is deleted."""
        patient = PatientFactory()
        address = AddressFactory(patient=patient)
        address_id = address.id

        patient.delete()

        assert not Address.objects.filter(id=address_id).exists()

    def test_address_str_representation(self):
        """Test string representation of address."""
        address = AddressFactory(
            village="Kimironko",
            cell="Bibare",
            sector="Kimironko",
            district="Gasabo",
        )
        address_str = str(address)
        assert "Kimironko" in address_str
        assert "Bibare" in address_str
        assert "Gasabo" in address_str

    def test_address_gps_coordinates_optional(self):
        """Test that GPS coordinates are optional."""
        address = AddressFactory(latitude=None, longitude=None)
        assert address.latitude is None
        assert address.longitude is None

    def test_address_with_valid_gps_coordinates(self):
        """Test address with valid GPS coordinates."""
        address = AddressFactory(
            latitude=-1.9578,  # Kigali latitude
            longitude=30.1127,  # Kigali longitude
        )
        assert address.latitude is not None
        assert address.longitude is not None


@pytest.mark.django_db
class TestEmergencyContactModel:
    """Test suite for EmergencyContact model."""

    def test_create_emergency_contact(self):
        """Test creating an emergency contact."""
        patient = PatientFactory()
        contact = EmergencyContactFactory(patient=patient)

        assert contact.id is not None
        assert contact.patient == patient
        assert contact.full_name
        assert contact.phone_number
        assert contact.relationship

    def test_patient_can_have_multiple_emergency_contacts(self):
        """Test that a patient can have multiple emergency contacts."""
        patient = PatientFactory()
        contact1 = EmergencyContactFactory(patient=patient)
        contact2 = EmergencyContactFactory(patient=patient)

        assert patient.emergency_contacts.count() == 2
        assert contact1 in patient.emergency_contacts.all()
        assert contact2 in patient.emergency_contacts.all()

    def test_emergency_contact_phone_number_format(self):
        """Test emergency contact phone number validation."""
        with pytest.raises(ValidationError):
            contact = EmergencyContactFactory.build(phone_number="invalid")
            contact.full_clean()

    def test_emergency_contact_primary_flag(self):
        """Test the is_primary flag on emergency contacts."""
        patient = PatientFactory()
        primary_contact = EmergencyContactFactory(patient=patient, is_primary=True)
        secondary_contact = EmergencyContactFactory(patient=patient, is_primary=False)

        assert primary_contact.is_primary is True
        assert secondary_contact.is_primary is False

    def test_emergency_contact_cascade_delete_with_patient(self):
        """Test that emergency contacts are deleted when patient is deleted."""
        patient = PatientFactory()
        contact = EmergencyContactFactory(patient=patient)
        contact_id = contact.id

        patient.delete()

        assert not EmergencyContact.objects.filter(id=contact_id).exists()

    def test_emergency_contact_ordering(self):
        """Test that emergency contacts are ordered by is_primary desc."""
        patient = PatientFactory()
        contact1 = EmergencyContactFactory(patient=patient, is_primary=False, full_name="B")
        contact2 = EmergencyContactFactory(patient=patient, is_primary=True, full_name="A")

        contacts = patient.emergency_contacts.all()
        assert contacts[0] == contact2  # Primary first
        assert contacts[1] == contact1

    def test_emergency_contact_str_representation(self):
        """Test string representation of emergency contact."""
        patient = PatientFactory(first_name="John", last_name="Doe")
        contact = EmergencyContactFactory(
            patient=patient,
            full_name="Jane Doe",
            relationship="spouse",
        )
        contact_str = str(contact)
        assert "Jane Doe" in contact_str
        assert "spouse" in contact_str
        assert "John Doe" in contact_str
