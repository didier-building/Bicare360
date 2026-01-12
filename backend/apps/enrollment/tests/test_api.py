"""
API tests for enrollment endpoints.
"""
import pytest
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.enrollment.models import Hospital, DischargeSummary
from apps.enrollment.tests.factories import HospitalFactory, DischargeSummaryFactory
from apps.patients.tests.factories import PatientFactory, UserFactory


@pytest.mark.django_db
class TestHospitalAPI:
    """Test Hospital API endpoints."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_list_hospitals(self):
        """Test listing hospitals."""
        HospitalFactory.create_batch(3)
        url = reverse('enrollment:hospital-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_create_hospital(self):
        """Test creating a hospital."""
        data = {
            'name': 'New Hospital',
            'code': 'NH01',
            'hospital_type': 'district',
            'province': 'Kigali',
            'district': 'Gasabo',
            'phone_number': '+250788123456',
            'status': 'active'
        }
        url = reverse('enrollment:hospital-list')
        response = self.client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Hospital.objects.filter(code='NH01').exists()
    
    def test_retrieve_hospital(self):
        """Test retrieving a single hospital."""
        hospital = HospitalFactory()
        url = reverse('enrollment:hospital-detail', args=[hospital.id])
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == hospital.id
    
    def test_update_hospital(self):
        """Test updating a hospital."""
        hospital = HospitalFactory()
        url = reverse('enrollment:hospital-detail', args=[hospital.id])
        data = {'name': 'Updated Hospital Name', 'code': hospital.code}
        response = self.client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        hospital.refresh_from_db()
        assert hospital.name == 'Updated Hospital Name'
    
    def test_filter_hospitals_by_type(self):
        """Test filtering hospitals by type."""
        HospitalFactory(hospital_type='referral')
        HospitalFactory(hospital_type='district')
        HospitalFactory(hospital_type='district')
        
        url = reverse('enrollment:hospital-list')
        response = self.client.get(url, {'hospital_type': 'district'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_search_hospitals_by_name(self):
        """Test searching hospitals by name."""
        HospitalFactory(name='Kigali Hospital')
        HospitalFactory(name='Butare Hospital')
        
        url = reverse('enrollment:hospital-list')
        response = self.client.get(url, {'search': 'Kigali'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Kigali' in response.data['results'][0]['name']
    
    def test_get_active_hospitals(self):
        """Test getting only active hospitals."""
        HospitalFactory(status='active')
        HospitalFactory(status='active')
        HospitalFactory(status='inactive')
        
        url = reverse('enrollment:hospital-active')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_get_hospitals_by_province(self):
        """Test getting hospitals by province."""
        HospitalFactory(province='Kigali', status='active')
        HospitalFactory(province='Kigali', status='active')
        HospitalFactory(province='Eastern', status='active')
        
        url = reverse('enrollment:hospital-by-province')
        response = self.client.get(url, {'province': 'Kigali'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2


@pytest.mark.django_db
class TestDischargeSummaryAPI:
    """Test DischargeSummary API endpoints."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_list_discharge_summaries(self):
        """Test listing discharge summaries."""
        DischargeSummaryFactory.create_batch(3)
        url = reverse('enrollment:dischargesummary-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_create_discharge_summary(self):
        """Test creating a discharge summary."""
        patient = PatientFactory()
        hospital = HospitalFactory()
        
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
        url = reverse('enrollment:dischargesummary-list')
        response = self.client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert DischargeSummary.objects.filter(patient=patient).exists()
    
    def test_retrieve_discharge_summary(self):
        """Test retrieving a single discharge summary."""
        discharge = DischargeSummaryFactory()
        url = reverse('enrollment:dischargesummary-detail', args=[discharge.id])
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == discharge.id
    
    def test_filter_by_risk_level(self):
        """Test filtering discharge summaries by risk level."""
        DischargeSummaryFactory(risk_level='high')
        DischargeSummaryFactory(risk_level='high')
        DischargeSummaryFactory(risk_level='low')
        
        url = reverse('enrollment:dischargesummary-list')
        response = self.client.get(url, {'risk_level': 'high'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_get_high_risk_summaries(self):
        """Test getting high-risk discharge summaries."""
        DischargeSummaryFactory(risk_level='high')
        DischargeSummaryFactory(risk_level='critical')
        DischargeSummaryFactory(risk_level='low')
        
        url = reverse('enrollment:dischargesummary-high-risk')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_get_recent_summaries(self):
        """Test getting recent discharge summaries."""
        today = date.today()
        DischargeSummaryFactory(
            admission_date=today - timedelta(days=10),
            discharge_date=today - timedelta(days=3)
        )
        DischargeSummaryFactory(
            admission_date=today - timedelta(days=12),
            discharge_date=today - timedelta(days=5)
        )
        DischargeSummaryFactory(
            admission_date=today - timedelta(days=17),
            discharge_date=today - timedelta(days=10)
        )
        
        url = reverse('enrollment:dischargesummary-recent')
        response = self.client.get(url, {'days': 7})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_get_needs_follow_up(self):
        """Test getting summaries that need follow-up."""
        DischargeSummaryFactory(follow_up_required=True)
        DischargeSummaryFactory(follow_up_required=True)
        DischargeSummaryFactory(follow_up_required=False)
        
        url = reverse('enrollment:dischargesummary-needs-follow-up')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_risk_analysis_endpoint(self):
        """Test risk analysis endpoint."""
        discharge = DischargeSummaryFactory(
            risk_level='high',
            risk_factors='Elderly patient with multiple comorbidities',
            warning_signs='Chest pain, shortness of breath'
        )
        
        url = reverse('enrollment:dischargesummary-risk-analysis', args=[discharge.id])
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['risk_level'] == 'high'
        assert response.data['is_high_risk'] is True
        assert 'risk_factors' in response.data
        assert 'warning_signs' in response.data
