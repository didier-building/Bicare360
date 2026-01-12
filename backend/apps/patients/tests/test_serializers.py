"""
Unit tests for Patient serializers.
Tests serializer validation, data transformation, and edge cases.
"""
import pytest
from django.core.exceptions import ValidationError
from apps.patients.serializers import (
    PatientListSerializer,
    PatientDetailSerializer,
    PatientCreateSerializer,
    AddressSerializer,
    EmergencyContactSerializer,
)
from apps.patients.tests.factories import (
    PatientFactory,
    AddressFactory,
    EmergencyContactFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestEmergencyContactSerializer:
    """Unit tests for EmergencyContactSerializer."""

    def test_serialize_emergency_contact(self):
        """Test serializing an emergency contact."""
        contact = EmergencyContactFactory()
        serializer = EmergencyContactSerializer(contact)
        
        data = serializer.data
        assert data["full_name"] == contact.full_name
        assert data["relationship"] == contact.relationship
        assert data["phone_number"] == contact.phone_number
        assert "id" in data
        assert "created_at" in data

    def test_deserialize_valid_emergency_contact(self):
        """Test deserializing valid emergency contact data."""
        data = {
            "full_name": "John Doe",
            "relationship": "spouse",
            "phone_number": "+250788123456",
            "is_primary": True,
        }
        serializer = EmergencyContactSerializer(data=data)
        assert serializer.is_valid()

    def test_invalid_phone_number_format(self):
        """Test that invalid phone number is rejected."""
        data = {
            "full_name": "John Doe",
            "relationship": "spouse",
            "phone_number": "123456",  # Invalid
        }
        serializer = EmergencyContactSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestAddressSerializer:
    """Unit tests for AddressSerializer."""

    def test_serialize_address(self):
        """Test serializing an address."""
        address = AddressFactory()
        serializer = AddressSerializer(address)
        
        data = serializer.data
        assert data["province"] == address.province
        assert data["district"] == address.district
        assert data["sector"] == address.sector
        assert data["cell"] == address.cell
        assert data["village"] == address.village

    def test_gps_coordinates_validation_both_required(self):
        """Test that both latitude and longitude must be provided together."""
        data = {
            "province": "Kigali",
            "district": "Gasabo",
            "sector": "Kimironko",
            "cell": "Bibare",
            "village": "Kibagabaga",
            "latitude": -1.9578,
            # longitude missing
        }
        serializer = AddressSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_gps_coordinates_both_provided(self):
        """Test that both coordinates can be provided successfully."""
        data = {
            "province": "Kigali",
            "district": "Gasabo",
            "sector": "Kimironko",
            "cell": "Bibare",
            "village": "Kibagabaga",
            "latitude": -1.9578,
            "longitude": 30.1127,
        }
        serializer = AddressSerializer(data=data)
        assert serializer.is_valid()

    def test_gps_coordinates_both_omitted(self):
        """Test that both coordinates can be omitted."""
        data = {
            "province": "Kigali",
            "district": "Gasabo",
            "sector": "Kimironko",
            "cell": "Bibare",
            "village": "Kibagabaga",
        }
        serializer = AddressSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestPatientListSerializer:
    """Unit tests for PatientListSerializer (lightweight)."""

    def test_serialize_patient_list(self):
        """Test serializing patient for list view."""
        patient = PatientFactory()
        serializer = PatientListSerializer(patient)
        
        data = serializer.data
        assert data["full_name"] == patient.full_name
        assert data["national_id"] == patient.national_id
        assert data["phone_number"] == patient.phone_number
        assert "age" in data
        assert "id" in data
        # Should NOT include detailed fields
        assert "address" not in data
        assert "emergency_contacts" not in data

    def test_multiple_patients_serialization(self):
        """Test serializing multiple patients."""
        patients = [PatientFactory() for _ in range(5)]
        serializer = PatientListSerializer(patients, many=True)
        
        data = serializer.data
        assert len(data) == 5
        for item in data:
            assert "full_name" in item
            assert "national_id" in item


@pytest.mark.django_db
class TestPatientDetailSerializer:
    """Unit tests for PatientDetailSerializer."""

    def test_serialize_patient_detail_with_address(self):
        """Test serializing patient with address."""
        patient = PatientFactory()
        address = AddressFactory(patient=patient)
        serializer = PatientDetailSerializer(patient)
        
        data = serializer.data
        assert data["address"] is not None
        assert data["address"]["province"] == address.province
        assert data["address"]["district"] == address.district

    def test_serialize_patient_detail_with_emergency_contacts(self):
        """Test serializing patient with emergency contacts."""
        patient = PatientFactory()
        contact1 = EmergencyContactFactory(patient=patient)
        contact2 = EmergencyContactFactory(patient=patient)
        
        serializer = PatientDetailSerializer(patient)
        data = serializer.data
        
        assert len(data["emergency_contacts"]) == 2
        contact_names = [c["full_name"] for c in data["emergency_contacts"]]
        assert contact1.full_name in contact_names
        assert contact2.full_name in contact_names

    def test_create_patient_with_nested_address(self, api_client):
        """Test creating patient with nested address."""
        user = UserFactory()
        api_client.force_authenticate(user=user)
        
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
            "address": {
                "province": "Kigali",
                "district": "Gasabo",
                "sector": "Kimironko",
                "cell": "Bibare",
                "village": "Kibagabaga",
            },
        }
        
        serializer = PatientDetailSerializer(
            data=data,
            context={"request": type("Request", (), {"user": user})()},
        )
        assert serializer.is_valid(), serializer.errors
        patient = serializer.save()
        
        assert patient.address is not None
        assert patient.address.province == "Kigali"

    def test_create_patient_with_nested_emergency_contacts(self):
        """Test creating patient with nested emergency contacts."""
        user = UserFactory()
        
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
            "emergency_contacts": [
                {
                    "full_name": "Jane Doe",
                    "relationship": "spouse",
                    "phone_number": "+250788654321",
                    "is_primary": True,
                },
                {
                    "full_name": "Bob Smith",
                    "relationship": "friend",
                    "phone_number": "+250788111222",
                    "is_primary": False,
                },
            ],
        }
        
        serializer = PatientDetailSerializer(
            data=data,
            context={"request": type("Request", (), {"user": user})()},
        )
        assert serializer.is_valid(), serializer.errors
        patient = serializer.save()
        
        assert patient.emergency_contacts.count() == 2

    def test_update_patient_address(self):
        """Test updating patient's address."""
        user = UserFactory()
        patient = PatientFactory()
        address = AddressFactory(patient=patient)
        
        data = {
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": str(patient.date_of_birth),
            "gender": patient.gender,
            "national_id": patient.national_id,
            "phone_number": patient.phone_number,
            "address": {
                "province": "Eastern",  # Changed
                "district": "Rwamagana",  # Changed
                "sector": address.sector,
                "cell": address.cell,
                "village": address.village,
            },
        }
        
        serializer = PatientDetailSerializer(
            patient,
            data=data,
            context={"request": type("Request", (), {"user": user})()},
        )
        assert serializer.is_valid(), serializer.errors
        updated_patient = serializer.save()
        
        updated_patient.address.refresh_from_db()
        assert updated_patient.address.province == "Eastern"
        assert updated_patient.address.district == "Rwamagana"


@pytest.mark.django_db
class TestPatientCreateSerializer:
    """Unit tests for PatientCreateSerializer."""

    def test_create_patient_minimal_fields(self):
        """Test creating patient with minimal required fields."""
        user = UserFactory()
        
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
        }
        
        serializer = PatientCreateSerializer(
            data=data,
            context={"request": type("Request", (), {"user": user})()},
        )
        assert serializer.is_valid(), serializer.errors
        patient = serializer.save()
        
        assert patient.first_name == "John"
        assert patient.enrolled_by == user

    def test_duplicate_national_id_validation(self):
        """Test that duplicate national ID is rejected."""
        PatientFactory(national_id="1234567890123456")
        user = UserFactory()
        
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",  # Duplicate
            "phone_number": "+250788123456",
        }
        
        serializer = PatientCreateSerializer(
            data=data,
            context={"request": type("Request", (), {"user": user})()},
        )
        assert not serializer.is_valid()
        assert "national_id" in serializer.errors
