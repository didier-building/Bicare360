"""
Integration tests for Patient API endpoints.
Tests full request/response cycle including authentication, permissions, and database.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from apps.patients.models import Patient, Address, EmergencyContact
from apps.patients.tests.factories import (
    PatientFactory,
    AddressFactory,
    EmergencyContactFactory,
    UserFactory,
)


@pytest.mark.django_db
@pytest.mark.integration
class TestPatientListAPI:
    """Integration tests for patient list endpoint."""

    def test_list_patients_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        url = reverse("patients:patient-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_patients_authenticated(self, authenticated_client):
        """Test listing patients with authentication."""
        PatientFactory.create_batch(5)
        url = reverse("patients:patient-list")
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5

    def test_list_patients_pagination(self, authenticated_client):
        """Test that patient list is paginated."""
        PatientFactory.create_batch(25)
        url = reverse("patients:patient-list")
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
        assert response.data["count"] == 25
        assert len(response.data["results"]) == 20  # Default page size

    def test_search_patients_by_name(self, authenticated_client):
        """Test searching patients by name."""
        PatientFactory(first_name="John", last_name="Doe")
        PatientFactory(first_name="Jane", last_name="Smith")
        
        url = reverse("patients:patient-list")
        response = authenticated_client.get(url, {"search": "John"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["full_name"] == "John Doe"

    def test_filter_patients_by_gender(self, authenticated_client):
        """Test filtering patients by gender."""
        PatientFactory.create_batch(3, gender="M")
        PatientFactory.create_batch(2, gender="F")
        
        url = reverse("patients:patient-list")
        response = authenticated_client.get(url, {"gender": "M"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_filter_patients_by_active_status(self, authenticated_client):
        """Test filtering patients by active status."""
        PatientFactory.create_batch(3, is_active=True)
        PatientFactory.create_batch(2, is_active=False)
        
        url = reverse("patients:patient-list")
        response = authenticated_client.get(url, {"is_active": "true"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_order_patients_by_enrolled_date(self, authenticated_client):
        """Test ordering patients by enrollment date."""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        patient3 = PatientFactory()
        
        url = reverse("patients:patient-list")
        response = authenticated_client.get(url, {"ordering": "-enrolled_date"})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["id"] == patient3.id  # Most recent first


@pytest.mark.django_db
@pytest.mark.integration
class TestPatientCreateAPI:
    """Integration tests for creating patients."""

    def test_create_patient_success(self, authenticated_client):
        """Test successful patient creation."""
        url = reverse("patients:patient-list")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
        }
        
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["first_name"] == "John"
        assert response.data["last_name"] == "Doe"
        
        # Verify patient created in database
        assert Patient.objects.filter(national_id="1234567890123456").exists()

    def test_create_patient_with_invalid_phone_number(self, authenticated_client):
        """Test creating patient with invalid phone number."""
        url = reverse("patients:patient-list")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "123456",  # Invalid
        }
        
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone_number" in response.data

    def test_create_patient_with_duplicate_national_id(self, authenticated_client):
        """Test creating patient with duplicate national ID."""
        PatientFactory(national_id="1234567890123456")
        
        url = reverse("patients:patient-list")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",  # Duplicate
            "phone_number": "+250788123456",
        }
        
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "national_id" in response.data

    def test_create_patient_with_kinyarwanda_names(self, authenticated_client):
        """Test creating patient with Kinyarwanda names."""
        url = reverse("patients:patient-list")
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "first_name_kinyarwanda": "Yohani",
            "last_name_kinyarwanda": "Umuhigi",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
            "language_preference": "kin",
        }
        
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        
        patient = Patient.objects.get(national_id="1234567890123456")
        assert patient.first_name_kinyarwanda == "Yohani"
        assert patient.language_preference == "kin"


@pytest.mark.django_db
@pytest.mark.integration
class TestPatientRetrieveAPI:
    """Integration tests for retrieving patient details."""

    def test_retrieve_patient_success(self, authenticated_client):
        """Test retrieving a specific patient."""
        patient = PatientFactory()
        url = reverse("patients:patient-detail", kwargs={"pk": patient.pk})
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == patient.id
        assert response.data["national_id"] == patient.national_id

    def test_retrieve_patient_with_address(self, authenticated_client):
        """Test retrieving patient with address."""
        patient = PatientFactory()
        address = AddressFactory(patient=patient)
        
        url = reverse("patients:patient-detail", kwargs={"pk": patient.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["address"] is not None
        assert response.data["address"]["province"] == address.province

    def test_retrieve_patient_with_emergency_contacts(self, authenticated_client):
        """Test retrieving patient with emergency contacts."""
        patient = PatientFactory()
        contact1 = EmergencyContactFactory(patient=patient)
        contact2 = EmergencyContactFactory(patient=patient)
        
        url = reverse("patients:patient-detail", kwargs={"pk": patient.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["emergency_contacts"]) == 2

    def test_retrieve_nonexistent_patient(self, authenticated_client):
        """Test retrieving a nonexistent patient returns 404."""
        url = reverse("patients:patient-detail", kwargs={"pk": 99999})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.integration
class TestPatientUpdateAPI:
    """Integration tests for updating patients."""

    def test_full_update_patient(self, authenticated_client):
        """Test full update (PUT) of a patient."""
        patient = PatientFactory()
        url = reverse("patients:patient-detail", kwargs={"pk": patient.pk})
        
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "date_of_birth": str(patient.date_of_birth),
            "gender": patient.gender,
            "national_id": patient.national_id,
            "phone_number": "+250788999999",  # Updated
        }
        
        response = authenticated_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        patient.refresh_from_db()
        assert patient.first_name == "Updated"
        assert patient.phone_number == "+250788999999"

    def test_partial_update_patient(self, authenticated_client):
        """Test partial update (PATCH) of a patient."""
        patient = PatientFactory()
        url = reverse("patients:patient-detail", kwargs={"pk": patient.pk})
        
        data = {"phone_number": "+250788111111"}
        response = authenticated_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.phone_number == "+250788111111"


@pytest.mark.django_db
@pytest.mark.integration
class TestPatientDeleteAPI:
    """Integration tests for deleting patients."""

    def test_delete_patient(self, authenticated_client):
        """Test deleting a patient."""
        patient = PatientFactory()
        url = reverse("patients:patient-detail", kwargs={"pk": patient.pk})
        
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Patient.objects.filter(pk=patient.pk).exists()


@pytest.mark.django_db
@pytest.mark.integration
class TestPatientCustomActions:
    """Integration tests for custom patient actions."""

    def test_deactivate_patient(self, authenticated_client):
        """Test deactivating a patient (soft delete)."""
        patient = PatientFactory(is_active=True)
        url = reverse("patients:patient-deactivate", kwargs={"pk": patient.pk})
        
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        patient.refresh_from_db()
        assert patient.is_active is False

    def test_activate_patient(self, authenticated_client):
        """Test reactivating a patient."""
        patient = PatientFactory(is_active=False)
        url = reverse("patients:patient-activate", kwargs={"pk": patient.pk})
        
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        patient.refresh_from_db()
        assert patient.is_active is True

    def test_patient_stats(self, authenticated_client):
        """Test retrieving patient statistics."""
        PatientFactory.create_batch(3, is_active=True, gender="M")
        PatientFactory.create_batch(2, is_active=True, gender="F")
        PatientFactory.create_batch(1, is_active=False, gender="M")
        
        url = reverse("patients:patient-stats")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_patients"] == 6
        assert response.data["active_patients"] == 5
        assert response.data["inactive_patients"] == 1
        assert response.data["by_gender"]["M"] == 4
        assert response.data["by_gender"]["F"] == 2


@pytest.mark.django_db
@pytest.mark.integration
class TestAddressAPI:
    """Integration tests for Address endpoints."""

    def test_list_addresses(self, authenticated_client):
        """Test listing all addresses."""
        AddressFactory.create_batch(3)
        url = reverse("patients:address-list")
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_filter_addresses_by_province(self, authenticated_client):
        """Test filtering addresses by province."""
        AddressFactory.create_batch(2, province="Kigali")
        AddressFactory.create_batch(1, province="Eastern")
        
        url = reverse("patients:address-list")
        response = authenticated_client.get(url, {"province": "Kigali"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


@pytest.mark.django_db
@pytest.mark.integration
class TestEmergencyContactAPI:
    """Integration tests for EmergencyContact endpoints."""

    def test_list_emergency_contacts(self, authenticated_client):
        """Test listing all emergency contacts."""
        EmergencyContactFactory.create_batch(3)
        url = reverse("patients:emergency-contact-list")
        
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_filter_emergency_contacts_by_patient(self, authenticated_client):
        """Test filtering emergency contacts by patient."""
        patient = PatientFactory()
        EmergencyContactFactory.create_batch(2, patient=patient)
        EmergencyContactFactory.create_batch(1)  # Different patient
        
        url = reverse("patients:emergency-contact-list")
        response = authenticated_client.get(url, {"patient": patient.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_filter_emergency_contacts_by_primary(self, authenticated_client):
        """Test filtering emergency contacts by primary flag."""
        EmergencyContactFactory.create_batch(2, is_primary=True)
        EmergencyContactFactory.create_batch(3, is_primary=False)
        
        url = reverse("patients:emergency-contact-list")
        response = authenticated_client.get(url, {"is_primary": "true"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
