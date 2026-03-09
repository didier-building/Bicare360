"""API tests for nursing app."""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apps.nursing.models import (
    NurseProfile, PatientAlert, NursePatientAssignment
)
from apps.nursing.tests.factories import (
    NurseProfileFactory, PatientAlertFactory,
    NursePatientAssignmentFactory, UserFactory
)
from apps.patients.tests.factories import PatientFactory
from apps.enrollment.tests.factories import DischargeSummaryFactory


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def authenticated_user(api_client):
    """Create and authenticate a regular user (not a nurse)."""
    user = UserFactory(username='testuser')
    user.set_password('password123')
    user.save()
    api_client.force_authenticate(user=user)
    return user

@pytest.fixture
def authenticated_nurse(api_client):
    """Create and authenticate a nurse user."""
    user = UserFactory(username='testnurse')
    user.set_password('password123')
    user.save()
    nurse = NurseProfileFactory(user=user)
    api_client.force_authenticate(user=user)
    return user, nurse


@pytest.mark.django_db
class TestPatientAlertAPI:
    """Test cases for PatientAlert API endpoints."""

    def test_list_alerts(self, api_client, authenticated_nurse):
        """Test listing all patient alerts."""
        PatientAlertFactory.create_batch(3)
        
        url = reverse('patientalert-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 3

    def test_create_alert(self, api_client, authenticated_nurse):
        """Test creating a new patient alert."""
        user, nurse = authenticated_nurse
        patient = PatientFactory()
        nurse = NurseProfileFactory()
        
        url = reverse('patientalert-list')
        data = {
            'patient': patient.id,
            'alert_type': 'missed_medication',
            'severity': 'high',
            'title': 'Missed Morning Medication',
            'description': 'High blood pressure medication not taken',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
        assert response.data['alert_type'] == 'missed_medication'
        assert response.data['severity'] == 'high'

    def test_retrieve_alert(self, api_client, authenticated_nurse):
        """Test retrieving a specific alert."""
        user, nurse = authenticated_nurse
        alert = PatientAlertFactory()
        
        url = reverse('patientalert-detail', args=[alert.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == alert.id

    def test_update_alert(self, api_client, authenticated_nurse):
        """Test updating an alert."""
        user, nurse = authenticated_nurse
        alert = PatientAlertFactory(status='new')
        
        url = reverse('patientalert-detail', args=[alert.id])
        data = {
            'patient_id': alert.patient.id,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'title': alert.title,
            'description': 'Updated description',
            'status': 'assigned'
        }
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'assigned'

    def test_delete_alert(self, api_client, authenticated_nurse):
        """Test deleting an alert."""
        user, nurse = authenticated_nurse
        alert = PatientAlertFactory()
        
        url = reverse('patientalert-detail', args=[alert.id])
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not PatientAlert.objects.filter(id=alert.id).exists()

    def test_acknowledge_alert(self, api_client, authenticated_nurse):
        """Test acknowledging an alert."""
        user, nurse = authenticated_nurse
        alert = PatientAlertFactory(status='new')
        
        url = reverse('patientalert-acknowledge', args=[alert.id])
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        alert.refresh_from_db()
        assert alert.status == 'in_progress'

    def test_resolve_alert(self, api_client, authenticated_nurse):
        """Test resolving an alert."""
        user, nurse = authenticated_nurse
        alert = PatientAlertFactory(status='in_progress')
        
        url = reverse('patientalert-resolve', args=[alert.id])
        data = {'resolution_notes': 'Issue resolved'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        alert.refresh_from_db()
        assert alert.status == 'resolved'


@pytest.mark.django_db
class TestNursePatientAssignmentAPI:
    """Test cases for NursePatientAssignment API endpoints."""

    def test_list_assignments(self, api_client, authenticated_user):
        """Test listing all assignments."""
        NursePatientAssignmentFactory.create_batch(3)
        
        url = reverse('nursepatientassignment-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_create_assignment(self, api_client, authenticated_user):
        """Test creating a new assignment."""
        nurse = NurseProfileFactory()
        patient = PatientFactory()
        discharge = DischargeSummaryFactory(patient=patient)
        
        url = reverse('nursepatientassignment-list')
        data = {
            'nurse_id': nurse.id,
            'patient_id': patient.id,
            'discharge_summary_id': discharge.id,
            'status': 'active',
            'priority': 2
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
        assert response.data['status'] == 'active'
        assert response.data['priority'] == 2

    def test_retrieve_assignment(self, api_client, authenticated_user):
        """Test retrieving a specific assignment."""
        assignment = NursePatientAssignmentFactory()
        
        url = reverse('nursepatientassignment-detail', args=[assignment.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == assignment.id

    def test_my_patients(self, api_client, authenticated_user):
        """Test getting nurse's assigned patients."""
        # Create nurse profile for authenticated user
        nurse = NurseProfileFactory(user=authenticated_user)
        
        # Create assignments for this nurse
        NursePatientAssignmentFactory.create_batch(2, nurse=nurse, status='active')
        # Create assignment for another nurse
        NursePatientAssignmentFactory()
        
        url = reverse('nursepatientassignment-my-patients')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


@pytest.mark.django_db
class TestNurseProfileAPI:
    """Test cases for NurseProfile API endpoints."""

    def test_list_nurse_profiles(self, api_client, authenticated_nurse):
        """Test listing all nurse profiles."""
        # authenticated_nurse already creates 1 nurse, create 2 more
        NurseProfileFactory.create_batch(2)
        
        url = reverse('nurseprofile-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 3  # At least 3 nurses

    def test_create_nurse_profile(self, api_client, authenticated_user):
        """Test creating a nurse profile."""
        user = UserFactory()
        
        url = reverse('nurseprofile-list')
        data = {
            'user_id': user.id,
            'license_number': 'RN12345',
            'phone_number': '+250788123456',
            'specialization': 'ICU',
            'current_shift': 'morning',
            'status': 'available'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['specialization'] == 'ICU'

    def test_retrieve_nurse_profile(self, api_client, authenticated_user):
        """Test retrieving a nurse profile."""
        nurse = NurseProfileFactory()
        
        url = reverse('nurseprofile-detail', args=[nurse.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == nurse.id


@pytest.mark.django_db
class TestAlertFiltering:
    """Test alert filtering and search."""

    def test_filter_by_status(self, api_client, authenticated_nurse):
        """Test filtering alerts by status."""
        PatientAlertFactory(status='new')
        PatientAlertFactory(status='in_progress')
        PatientAlertFactory(status='resolved')
        
        url = reverse('patientalert-list')
        response = api_client.get(url, {'status': 'new'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
        for result in response.data['results']:
            assert result['status'] == 'new'

    def test_filter_by_severity(self, api_client, authenticated_nurse):
        """Test filtering alerts by severity."""
        PatientAlertFactory(severity='low')
        PatientAlertFactory(severity='high')
        PatientAlertFactory(severity='critical')
        
        url = reverse('patientalert-list')
        response = api_client.get(url, {'severity': 'critical'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
        for result in response.data['results']:
            assert result['severity'] == 'critical'

    def test_filter_by_alert_type(self, api_client, authenticated_nurse):
        """Test filtering alerts by type."""
        PatientAlertFactory(alert_type='vital_signs')
        PatientAlertFactory(alert_type='medication')
        PatientAlertFactory(alert_type='emergency')
        
        url = reverse('patientalert-list')
        response = api_client.get(url, {'alert_type': 'emergency'})
        
        assert response.status_code == status.HTTP_200_OK
        # Check that all returned alerts have the correct type
        for alert in response.data['results']:
            assert alert['alert_type'] == 'emergency'
        assert len(response.data['results']) >= 1
