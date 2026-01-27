"""
Tests for Medication Adherence API endpoints.
Following TDD approach - tests first, then implementation.
"""
import pytest
from datetime import date, time, timedelta
from django.utils import timezone
from rest_framework import status
from apps.medications.models import MedicationAdherence


@pytest.mark.django_db
class TestAdherenceListAPI:
    """Test GET /api/v1/adherence/ endpoint"""
    
    def test_list_adherence_records(self, authenticated_client, adherence_factory):
        """Should return list of adherence records"""
        # Create 3 adherence records
        adherence_factory.create_batch(3)
        
        response = authenticated_client.get('/api/v1/adherence/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3
    
    def test_list_adherence_filtered_by_patient(self, authenticated_client, adherence_factory, patient_factory):
        """Should filter adherence records by patient"""
        patient1 = patient_factory()
        patient2 = patient_factory()
        
        adherence_factory.create_batch(2, patient=patient1)
        adherence_factory(patient=patient2)
        
        response = authenticated_client.get(f'/api/v1/adherence/?patient={patient1.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_list_adherence_filtered_by_status(self, authenticated_client, adherence_factory):
        """Should filter adherence records by status"""
        adherence_factory.create_batch(2, status='taken')
        adherence_factory(status='missed')
        adherence_factory(status='scheduled')
        
        response = authenticated_client.get('/api/v1/adherence/?status=taken')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2


@pytest.mark.django_db
class TestMarkTakenAPI:
    """Test POST /api/v1/adherence/{id}/mark_taken/ endpoint"""
    
    def test_mark_adherence_as_taken(self, authenticated_client, adherence_factory):
        """Should mark adherence record as taken with timestamp"""
        adherence = adherence_factory(status='scheduled')
        
        response = authenticated_client.post(f'/api/v1/adherence/{adherence.id}/mark_taken/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'taken'
        assert response.data['taken_at'] is not None
        
        # Verify in database
        adherence.refresh_from_db()
        assert adherence.status == 'taken'
        assert adherence.taken_at is not None
    
    def test_mark_taken_requires_authentication(self, api_client, adherence_factory):
        """Should require authentication"""
        adherence = adherence_factory()
        
        response = api_client.post(f'/api/v1/adherence/{adherence.id}/mark_taken/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMarkMissedAPI:
    """Test POST /api/v1/adherence/{id}/mark_missed/ endpoint"""
    
    def test_mark_adherence_as_missed(self, authenticated_client, adherence_factory):
        """Should mark adherence record as missed"""
        adherence = adherence_factory(status='scheduled')
        
        response = authenticated_client.post(
            f'/api/v1/adherence/{adherence.id}/mark_missed/',
            {'reason': 'Forgot to take medication'}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'missed'
        assert response.data['reason_missed'] == 'Forgot to take medication'
        
        # Verify in database
        adherence.refresh_from_db()
        assert adherence.status == 'missed'
        assert adherence.reason_missed == 'Forgot to take medication'
    
    def test_mark_missed_without_reason(self, authenticated_client, adherence_factory):
        """Should mark as missed even without reason"""
        adherence = adherence_factory(status='scheduled')
        
        response = authenticated_client.post(f'/api/v1/adherence/{adherence.id}/mark_missed/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'missed'


@pytest.mark.django_db
class TestOverdueAPI:
    """Test GET /api/v1/adherence/overdue/ endpoint"""
    
    def test_get_overdue_adherence_records(self, authenticated_client, adherence_factory):
        """Should return only overdue scheduled records"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Overdue records
        overdue1 = adherence_factory(
            scheduled_date=yesterday,
            status='scheduled'
        )
        overdue2 = adherence_factory(
            scheduled_date=today,
            scheduled_time=time(8, 0),
            status='scheduled'
        )
        
        # Not overdue
        adherence_factory(scheduled_date=tomorrow, status='scheduled')
        adherence_factory(scheduled_date=yesterday, status='taken')
        
        response = authenticated_client.get('/api/v1/adherence/overdue/')
        
        assert response.status_code == status.HTTP_200_OK
        # Note: The exact count depends on current time for today's records
        assert response.data['count'] >= 1  # At least yesterday's overdue
    
    def test_overdue_excludes_completed_records(self, authenticated_client, adherence_factory):
        """Should not include taken/missed records even if date has passed"""
        yesterday = date.today() - timedelta(days=1)
        
        adherence_factory(scheduled_date=yesterday, status='taken')
        adherence_factory(scheduled_date=yesterday, status='missed')
        overdue = adherence_factory(scheduled_date=yesterday, status='scheduled')
        
        response = authenticated_client.get('/api/v1/adherence/overdue/')
        
        assert response.status_code == status.HTTP_200_OK
        overdue_ids = [record['id'] for record in response.data['results']]
        assert overdue.id in overdue_ids


@pytest.mark.django_db
class TestAdherenceStatsAPI:
    """Test GET /api/v1/adherence/stats/ endpoint"""
    
    def test_get_adherence_statistics(self, authenticated_client, adherence_factory):
        """Should return adherence statistics"""
        # Create adherence records with different statuses
        adherence_factory.create_batch(5, status='taken')
        adherence_factory.create_batch(2, status='missed')
        adherence_factory(status='scheduled')
        adherence_factory(status='skipped')
        adherence_factory(status='late')
        
        response = authenticated_client.get('/api/v1/adherence/stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 10
        assert response.data['taken'] == 5
        assert response.data['missed'] == 2
        assert response.data['scheduled'] == 1
        assert response.data['skipped'] == 1
        assert response.data['late'] == 1
        assert response.data['adherence_rate'] == 50.0  # 5/10 * 100
    
    def test_stats_filtered_by_patient(self, authenticated_client, adherence_factory, patient_factory):
        """Should return stats filtered by patient"""
        patient1 = patient_factory()
        patient2 = patient_factory()
        
        adherence_factory.create_batch(3, patient=patient1, status='taken')
        adherence_factory(patient=patient1, status='missed')
        adherence_factory.create_batch(2, patient=patient2, status='taken')
        
        response = authenticated_client.get(f'/api/v1/adherence/stats/?patient={patient1.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 4
        assert response.data['taken'] == 3
        assert response.data['adherence_rate'] == 75.0


@pytest.mark.django_db
class TestCreateAdherenceAPI:
    """Test POST /api/v1/adherence/ endpoint"""
    
    def test_create_adherence_record(self, authenticated_client, prescription_factory, patient_factory):
        """Should create new adherence record"""
        prescription = prescription_factory()
        patient = prescription.patient
        
        data = {
            'prescription': prescription.id,
            'patient': patient.id,
            'scheduled_date': date.today().isoformat(),
            'scheduled_time': '09:00:00',
            'status': 'scheduled'
        }
        
        response = authenticated_client.post('/api/v1/adherence/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['prescription'] == prescription.id
        assert response.data['patient'] == patient.id
        assert response.data['status'] == 'scheduled'
        
        # Verify in database
        assert MedicationAdherence.objects.filter(prescription=prescription).exists()
