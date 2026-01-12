"""
Deep unit tests for Patient API views.
Tests view logic, permission handling, query optimization, and edge cases.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory
from apps.patients.views import PatientViewSet, AddressViewSet, EmergencyContactViewSet
from apps.patients.tests.factories import (
    PatientFactory,
    AddressFactory,
    EmergencyContactFactory,
    UserFactory,
)

User = get_user_model()


@pytest.mark.django_db
class TestPatientViewSetQueryOptimization:
    """Test query optimization and performance."""

    def test_queryset_uses_select_related(self):
        """Test that queryset uses select_related for enrolled_by and address."""
        viewset = PatientViewSet()
        queryset = viewset.get_queryset()
        
        # Check that select_related is used
        assert "enrolled_by" in str(queryset.query)
        assert "address" in str(queryset.query)

    def test_queryset_uses_prefetch_related(self):
        """Test that queryset uses prefetch_related for emergency_contacts."""
        viewset = PatientViewSet()
        queryset = viewset.get_queryset()
        
        # Verify prefetch_related is set
        assert len(queryset._prefetch_related_lookups) > 0

    def test_list_patients_query_count(self, authenticated_client, django_assert_num_queries):
        """Test that listing patients doesn't cause N+1 queries."""
        # Create patients with relations
        for _ in range(5):
            patient = PatientFactory()
            AddressFactory(patient=patient)
            EmergencyContactFactory.create_batch(2, patient=patient)

        # Should use optimized queries
        with django_assert_num_queries(3):  # 1 for patients, 1 for auth, 1 for count
            response = authenticated_client.get("/api/v1/patients/")
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPatientViewSetGetSerializerClass:
    """Test serializer class selection based on action."""

    def test_list_action_uses_list_serializer(self):
        """Test that list action uses PatientListSerializer."""
        viewset = PatientViewSet()
        viewset.action = "list"
        
        from apps.patients.serializers import PatientListSerializer
        assert viewset.get_serializer_class() == PatientListSerializer

    def test_create_action_uses_create_serializer(self):
        """Test that create action uses PatientCreateSerializer."""
        viewset = PatientViewSet()
        viewset.action = "create"
        
        from apps.patients.serializers import PatientCreateSerializer
        assert viewset.get_serializer_class() == PatientCreateSerializer

    def test_retrieve_action_uses_detail_serializer(self):
        """Test that retrieve action uses PatientDetailSerializer."""
        viewset = PatientViewSet()
        viewset.action = "retrieve"
        
        from apps.patients.serializers import PatientDetailSerializer
        assert viewset.get_serializer_class() == PatientDetailSerializer

    def test_update_action_uses_detail_serializer(self):
        """Test that update action uses PatientDetailSerializer."""
        viewset = PatientViewSet()
        viewset.action = "update"
        
        from apps.patients.serializers import PatientDetailSerializer
        assert viewset.get_serializer_class() == PatientDetailSerializer


@pytest.mark.django_db
class TestPatientViewSetCustomActions:
    """Deep tests for custom actions (deactivate, activate, stats)."""

    def test_deactivate_action_changes_status(self, authenticated_client):
        """Test that deactivate action sets is_active to False."""
        patient = PatientFactory(is_active=True)
        
        response = authenticated_client.post(f"/api/v1/patients/{patient.pk}/deactivate/")
        
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.is_active is False

    def test_activate_action_changes_status(self, authenticated_client):
        """Test that activate action sets is_active to True."""
        patient = PatientFactory(is_active=False)
        
        response = authenticated_client.post(f"/api/v1/patients/{patient.pk}/activate/")
        
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.is_active is True

    def test_deactivate_already_inactive_patient(self, authenticated_client):
        """Test deactivating an already inactive patient."""
        patient = PatientFactory(is_active=False)
        
        response = authenticated_client.post(f"/api/v1/patients/{patient.pk}/deactivate/")
        
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.is_active is False  # Still False

    def test_stats_action_returns_correct_counts(self):
        """Test that stats action returns accurate statistics."""
        # Create test data
        PatientFactory.create_batch(3, is_active=True, gender="M")
        PatientFactory.create_batch(2, is_active=True, gender="F")
        PatientFactory.create_batch(1, is_active=False, gender="M")
        
        user = UserFactory()
        factory = APIRequestFactory()
        request = factory.get("/api/v1/patients/stats/")
        request.user = user
        
        viewset = PatientViewSet()
        viewset.request = request
        
        response = viewset.stats(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_patients"] == 6
        assert response.data["active_patients"] == 5
        assert response.data["inactive_patients"] == 1
        assert response.data["by_gender"]["M"] == 4
        assert response.data["by_gender"]["F"] == 2

    def test_stats_with_no_patients(self):
        """Test stats action with no patients in database."""
        user = UserFactory()
        factory = APIRequestFactory()
        request = factory.get("/api/v1/patients/stats/")
        request.user = user
        
        viewset = PatientViewSet()
        viewset.request = request
        
        response = viewset.stats(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_patients"] == 0
        assert response.data["active_patients"] == 0


@pytest.mark.django_db
class TestPatientViewSetFiltering:
    """Deep tests for filtering functionality."""

    def test_filter_by_enrolled_by_user(self, authenticated_client):
        """Test filtering patients by who enrolled them."""
        user1 = UserFactory()
        user2 = UserFactory()
        
        PatientFactory.create_batch(2, enrolled_by=user1)
        PatientFactory.create_batch(3, enrolled_by=user2)
        
        response = authenticated_client.get(f"/api/v1/patients/?enrolled_by={user1.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_filter_by_language_preference(self, authenticated_client):
        """Test filtering by language preference."""
        PatientFactory.create_batch(3, language_preference="kin")
        PatientFactory.create_batch(2, language_preference="eng")
        
        response = authenticated_client.get("/api/v1/patients/?language_preference=kin")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_search_by_national_id(self, authenticated_client):
        """Test searching patients by national ID."""
        patient = PatientFactory(national_id="1234567890123456")
        PatientFactory.create_batch(3)  # Other patients
        
        response = authenticated_client.get("/api/v1/patients/?search=123456789")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["national_id"] == "1234567890123456"

    def test_search_by_email(self, authenticated_client):
        """Test searching patients by email."""
        patient = PatientFactory(email="unique.email@test.com")
        PatientFactory.create_batch(3)
        
        response = authenticated_client.get("/api/v1/patients/?search=unique.email")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_combined_filters_and_search(self, authenticated_client):
        """Test combining multiple filters and search."""
        PatientFactory(
            first_name="John",
            gender="M",
            is_active=True,
            language_preference="kin"
        )
        PatientFactory(
            first_name="Jane",
            gender="F",
            is_active=True,
            language_preference="kin"
        )
        PatientFactory(
            first_name="Bob",
            gender="M",
            is_active=False,
            language_preference="eng"
        )
        
        response = authenticated_client.get(
            "/api/v1/patients/?gender=M&is_active=true&search=John"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert "John" in response.data["results"][0]["full_name"]


@pytest.mark.django_db
class TestPatientViewSetOrdering:
    """Deep tests for ordering functionality."""

    def test_order_by_last_name_ascending(self, authenticated_client):
        """Test ordering patients by last name ascending."""
        PatientFactory(last_name="Zebra")
        PatientFactory(last_name="Apple")
        PatientFactory(last_name="Mango")
        
        response = authenticated_client.get("/api/v1/patients/?ordering=last_name")
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert "Apple" in results[0]["full_name"]

    def test_order_by_last_name_descending(self, authenticated_client):
        """Test ordering patients by last name descending."""
        PatientFactory(last_name="Zebra")
        PatientFactory(last_name="Apple")
        PatientFactory(last_name="Mango")
        
        response = authenticated_client.get("/api/v1/patients/?ordering=-last_name")
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert "Zebra" in results[0]["full_name"]

    def test_order_by_date_of_birth(self, authenticated_client):
        """Test ordering patients by date of birth."""
        from datetime import date
        
        PatientFactory(date_of_birth=date(1990, 1, 1))
        PatientFactory(date_of_birth=date(1985, 1, 1))
        PatientFactory(date_of_birth=date(1995, 1, 1))
        
        response = authenticated_client.get("/api/v1/patients/?ordering=date_of_birth")
        
        assert response.status_code == status.HTTP_200_OK
        # Oldest should be first
        assert response.data["results"][0]["age"] > response.data["results"][-1]["age"]


@pytest.mark.django_db
class TestAddressViewSetFiltering:
    """Deep tests for address filtering."""

    def test_filter_by_district(self, authenticated_client):
        """Test filtering addresses by district."""
        AddressFactory.create_batch(2, district="Gasabo")
        AddressFactory.create_batch(1, district="Kicukiro")
        
        response = authenticated_client.get("/api/v1/addresses/?district=Gasabo")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_filter_by_sector(self, authenticated_client):
        """Test filtering addresses by sector."""
        AddressFactory.create_batch(3, sector="Kimironko")
        AddressFactory.create_batch(2, sector="Remera")
        
        response = authenticated_client.get("/api/v1/addresses/?sector=Kimironko")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3


@pytest.mark.django_db
class TestEmergencyContactViewSetFiltering:
    """Deep tests for emergency contact filtering."""

    def test_filter_by_relationship(self, authenticated_client):
        """Test filtering by relationship type."""
        EmergencyContactFactory.create_batch(2, relationship="spouse")
        EmergencyContactFactory.create_batch(3, relationship="parent")
        EmergencyContactFactory.create_batch(1, relationship="sibling")
        
        response = authenticated_client.get(
            "/api/v1/emergency-contacts/?relationship=parent"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3


@pytest.mark.django_db
class TestViewSetErrorHandling:
    """Test error handling in viewsets."""

    def test_invalid_filter_parameter(self, authenticated_client):
        """Test that invalid filter parameters are handled gracefully."""
        response = authenticated_client.get("/api/v1/patients/?invalid_param=value")
        
        # Should still work, just ignore invalid param
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_ordering_field(self, authenticated_client):
        """Test ordering by invalid field."""
        PatientFactory.create_batch(3)
        
        # Try to order by non-existent field
        response = authenticated_client.get("/api/v1/patients/?ordering=nonexistent_field")
        
        # Should return 400 or ignore and use default
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_invalid_page_number(self, authenticated_client):
        """Test requesting invalid page number."""
        PatientFactory.create_batch(5)
        
        response = authenticated_client.get("/api/v1/patients/?page=999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_page_size(self, authenticated_client):
        """Test requesting invalid page size."""
        PatientFactory.create_batch(5)
        
        response = authenticated_client.get("/api/v1/patients/?page_size=invalid")
        
        # Should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
