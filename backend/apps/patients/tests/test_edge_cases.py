"""
Boundary and edge case tests for Patient models and API.
Tests limits, special characters, unicode, extreme values, and data validation.
"""
import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from apps.patients.models import Patient, Address, EmergencyContact
from apps.patients.tests.factories import PatientFactory, AddressFactory, UserFactory


@pytest.mark.django_db
class TestPatientBoundaryConditions:
    """Test boundary conditions and edge cases for Patient model."""

    def test_patient_with_very_old_date_of_birth(self):
        """Test patient with very old date of birth (120 years)."""
        old_date = date.today() - timedelta(days=365 * 120)
        patient = PatientFactory(date_of_birth=old_date)
        
        assert patient.age >= 119
        assert patient.age <= 120

    def test_patient_with_future_date_of_birth(self):
        """Test that future date of birth is allowed (for newborns registered before birth)."""
        future_date = date.today() + timedelta(days=30)
        patient = PatientFactory(date_of_birth=future_date)
        
        # Age calculation should handle negative ages
        assert patient.age <= 0

    def test_patient_born_today(self):
        """Test patient born today (age = 0)."""
        patient = PatientFactory(date_of_birth=date.today())
        assert patient.age == 0

    def test_patient_with_leap_year_birthday(self):
        """Test patient born on Feb 29 (leap year)."""
        patient = PatientFactory(date_of_birth=date(2000, 2, 29))
        assert patient.date_of_birth.month == 2
        assert patient.date_of_birth.day == 29

    def test_national_id_exactly_16_digits(self):
        """Test national ID with exactly 16 digits."""
        patient = PatientFactory(national_id="1234567890123456")
        patient.full_clean()  # Should not raise
        assert len(patient.national_id) == 16

    def test_national_id_15_digits_fails(self):
        """Test that 15-digit national ID fails validation."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(national_id="123456789012345")
            patient.full_clean()

    def test_national_id_17_digits_fails(self):
        """Test that 17-digit national ID fails validation."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(national_id="12345678901234567")
            patient.full_clean()

    def test_national_id_with_letters_fails(self):
        """Test that national ID with letters fails validation."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(national_id="123456789012345A")
            patient.full_clean()

    def test_phone_number_exactly_13_characters(self):
        """Test phone number with exactly 13 characters (+250XXXXXXXXX)."""
        patient = PatientFactory(phone_number="+250788123456")
        patient.full_clean()
        assert len(patient.phone_number) == 13

    def test_phone_number_without_plus_fails(self):
        """Test phone number without + prefix fails."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(phone_number="250788123456")
            patient.full_clean()

    def test_phone_number_with_wrong_country_code_fails(self):
        """Test phone number with wrong country code fails."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(phone_number="+251788123456")
            patient.full_clean()

    def test_very_long_first_name(self):
        """Test patient with very long first name (100 characters)."""
        long_name = "A" * 100
        patient = PatientFactory(first_name=long_name)
        assert len(patient.first_name) == 100

    def test_first_name_exceeding_max_length_truncated_by_db(self):
        """Test that first name exceeding 100 chars is handled by database."""
        long_name = "A" * 150
        # Django should truncate or raise error
        patient = PatientFactory.build(first_name=long_name)
        # This would fail at DB level if we try to save

    def test_empty_email_allowed(self):
        """Test that empty email is allowed (optional field)."""
        patient = PatientFactory(email="")
        patient.full_clean()
        assert patient.email == ""

    def test_valid_email_format(self):
        """Test valid email format."""
        patient = PatientFactory(email="test@example.com")
        patient.full_clean()
        assert "@" in patient.email

    def test_invalid_email_format_fails(self):
        """Test invalid email format fails validation."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(email="invalid-email")
            patient.full_clean()


@pytest.mark.django_db
class TestPatientUnicodeAndSpecialCharacters:
    """Test handling of Unicode and special characters."""

    def test_patient_with_kinyarwanda_characters(self):
        """Test patient with Kinyarwanda characters in name."""
        patient = PatientFactory(
            first_name_kinyarwanda="Uwimana",
            last_name_kinyarwanda="Mukamana"
        )
        assert patient.first_name_kinyarwanda == "Uwimana"

    def test_patient_with_french_accents(self):
        """Test patient with French accented characters."""
        patient = PatientFactory(
            first_name="François",
            last_name="Müller"
        )
        assert patient.first_name == "François"

    def test_patient_with_emoji_in_name(self):
        """Test that emoji in name is stored (though not recommended)."""
        patient = PatientFactory(first_name="John😊")
        # Should be stored as-is
        assert "😊" in patient.first_name

    def test_address_with_special_characters(self):
        """Test address with special characters."""
        address = AddressFactory(
            village="Village-Name (Section B)",
            landmarks="Near café & restaurant"
        )
        assert "(" in address.village
        assert "&" in address.landmarks


@pytest.mark.django_db
class TestAddressBoundaryConditions:
    """Test boundary conditions for Address model."""

    def test_gps_coordinates_at_rwanda_boundaries(self):
        """Test GPS coordinates at Rwanda's boundaries."""
        # Rwanda coordinates roughly: lat -2.8 to -1.0, lon 28.8 to 30.9
        address = AddressFactory(
            latitude=-1.9578,  # Kigali
            longitude=30.1127
        )
        assert -2.9 <= float(address.latitude) <= -0.9
        assert 28.7 <= float(address.longitude) <= 31.0

    def test_gps_coordinates_maximum_precision(self):
        """Test GPS coordinates with maximum decimal places (6)."""
        address = AddressFactory(
            latitude=-1.957845,  # 6 decimal places
            longitude=30.112765
        )
        # Verify precision is maintained
        lat_str = str(address.latitude)
        assert len(lat_str.split('.')[-1]) <= 6

    def test_very_long_street_address(self):
        """Test address with very long street address."""
        long_address = "A" * 500
        address = AddressFactory(street_address=long_address)
        # TextField should handle large text
        assert len(address.street_address) == 500

    def test_very_long_landmarks_description(self):
        """Test address with very long landmarks description."""
        long_landmarks = "Near " + ", ".join([f"landmark{i}" for i in range(100)])
        address = AddressFactory(landmarks=long_landmarks)
        assert "landmark99" in address.landmarks


@pytest.mark.django_db
class TestEmergencyContactBoundaryConditions:
    """Test boundary conditions for EmergencyContact model."""

    def test_multiple_primary_contacts_for_same_patient(self):
        """Test that multiple primary contacts can exist (business logic should handle)."""
        from apps.patients.tests.factories import EmergencyContactFactory
        patient = PatientFactory()
        
        # Create two primary contacts
        contact1 = EmergencyContactFactory(patient=patient, is_primary=True)
        contact2 = EmergencyContactFactory(patient=patient, is_primary=True)
        
        # Both should be saved successfully
        assert patient.emergency_contacts.filter(is_primary=True).count() == 2

    def test_emergency_contact_with_same_phone_as_patient(self):
        """Test emergency contact with same phone number as patient."""
        patient = PatientFactory(phone_number="+250788123456")
        from apps.patients.tests.factories import EmergencyContactFactory
        
        # This should be allowed
        contact = EmergencyContactFactory(
            patient=patient,
            phone_number="+250788123456"
        )
        assert contact.phone_number == patient.phone_number

    def test_very_long_contact_name(self):
        """Test emergency contact with very long name."""
        from apps.patients.tests.factories import EmergencyContactFactory
        long_name = "A" * 200
        contact = EmergencyContactFactory(full_name=long_name)
        assert len(contact.full_name) == 200


@pytest.mark.django_db
class TestAPIBoundaryConditions:
    """Test API boundary conditions and edge cases."""

    def test_create_patient_with_minimal_data(self, authenticated_client):
        """Test creating patient with only required fields."""
        data = {
            "first_name": "J",
            "last_name": "D",
            "date_of_birth": "2000-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
        }
        
        response = authenticated_client.post("/api/v1/patients/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_patient_with_all_fields(self, authenticated_client):
        """Test creating patient with all possible fields."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "first_name_kinyarwanda": "Yohani",
            "last_name_kinyarwanda": "Umuhigi",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
            "alt_phone_number": "+250788654321",
            "email": "john@example.com",
            "blood_type": "A+",
            "prefers_sms": True,
            "prefers_whatsapp": False,
            "language_preference": "kin",
        }
        
        response = authenticated_client.post("/api/v1/patients/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "john@example.com"

    def test_update_patient_with_empty_optional_fields(self, authenticated_client):
        """Test updating patient to clear optional fields."""
        patient = PatientFactory(email="old@example.com", alt_phone_number="+250788111111")
        
        data = {
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": str(patient.date_of_birth),
            "gender": patient.gender,
            "national_id": patient.national_id,
            "phone_number": patient.phone_number,
            "email": "",  # Clear email
            "alt_phone_number": "",  # Clear alt phone
        }
        
        response = authenticated_client.put(
            f"/api/v1/patients/{patient.pk}/",
            data,
            format="json"
        )
        
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.email == ""
        assert patient.alt_phone_number == ""

    def test_search_with_empty_string(self, authenticated_client):
        """Test searching with empty string."""
        PatientFactory.create_batch(5)
        response = authenticated_client.get("/api/v1/patients/?search=")
        
        assert response.status_code == status.HTTP_200_OK
        # Should return all patients
        assert len(response.data["results"]) == 5

    def test_search_with_special_characters(self, authenticated_client):
        """Test searching with special characters."""
        PatientFactory(first_name="O'Brien")
        
        response = authenticated_client.get("/api/v1/patients/?search=O'Brien")
        assert response.status_code == status.HTTP_200_OK

    def test_pagination_edge_cases(self, authenticated_client):
        """Test pagination with exactly page_size patients."""
        PatientFactory.create_batch(20)  # Exactly one page
        
        response = authenticated_client.get("/api/v1/patients/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 20
        assert response.data["next"] is None  # No next page

    def test_filter_with_null_values(self, authenticated_client):
        """Test filtering by fields that might be null."""
        PatientFactory(email="")
        PatientFactory(email="test@example.com")
        
        # Both should be returned in list
        response = authenticated_client.get("/api/v1/patients/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


@pytest.mark.django_db
class TestConcurrencyAndRaceConditions:
    """Test concurrent operations and potential race conditions."""

    def test_simultaneous_patient_creation_with_same_national_id(self, authenticated_client):
        """Test that simultaneous creation with same national ID is prevented."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
        }
        
        # First creation should succeed
        response1 = authenticated_client.post("/api/v1/patients/", data, format="json")
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second creation with same ID should fail
        response2 = authenticated_client.post("/api/v1/patients/", data, format="json")
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_patient_that_was_deleted(self, authenticated_client):
        """Test updating a patient that was deleted."""
        patient = PatientFactory()
        patient_id = patient.pk
        
        # Delete patient
        patient.delete()
        
        # Try to update
        data = {"phone_number": "+250788999999"}
        response = authenticated_client.patch(
            f"/api/v1/patients/{patient_id}/",
            data,
            format="json"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_activate_deactivated_patient_multiple_times(self, authenticated_client):
        """Test activating and deactivating patient multiple times."""
        patient = PatientFactory(is_active=True)
        
        # Deactivate
        response = authenticated_client.post(f"/api/v1/patients/{patient.pk}/deactivate/")
        assert response.status_code == status.HTTP_200_OK
        
        # Activate
        response = authenticated_client.post(f"/api/v1/patients/{patient.pk}/activate/")
        assert response.status_code == status.HTTP_200_OK
        
        # Deactivate again
        response = authenticated_client.post(f"/api/v1/patients/{patient.pk}/deactivate/")
        assert response.status_code == status.HTTP_200_OK
        
        patient.refresh_from_db()
        assert patient.is_active is False
