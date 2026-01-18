import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import time, timedelta

from apps.medications.models import Medication, Prescription, MedicationAdherence
from apps.patients.tests.factories import PatientFactory
from apps.enrollment.models import Hospital, DischargeSummary
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestMedicationAPI:
    """Test suite for Medication API endpoints"""
    
    def test_list_medications(self, authenticated_client):
        """Test listing all medications"""
        Medication.objects.create(
            name='Med1', generic_name='Generic1',
            dosage_form='tablet', strength='100mg'
        )
        Medication.objects.create(
            name='Med2', generic_name='Generic2',
            dosage_form='syrup', strength='5ml'
        )
        
        url = reverse('medications:medication-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_create_medication(self, authenticated_client):
        """Test creating a new medication"""
        url = reverse('medications:medication-list')
        data = {
            'name': 'Aspirin 100mg',
            'generic_name': 'Acetylsalicylic acid',
            'dosage_form': 'tablet',
            'strength': '100mg',
            'requires_prescription': False
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Medication.objects.count() == 1
        assert Medication.objects.first().name == 'Aspirin 100mg'
    
    def test_retrieve_medication(self, authenticated_client):
        """Test retrieving a single medication"""
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        
        url = reverse('medications:medication-detail', kwargs={'pk': medication.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Med'
    
    def test_update_medication(self, authenticated_client):
        """Test updating a medication"""
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        
        url = reverse('medications:medication-detail', kwargs={'pk': medication.pk})
        data = {'name': 'Updated Med', 'strength': '200mg'}
        
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        medication.refresh_from_db()
        assert medication.name == 'Updated Med'
    
    def test_delete_medication(self, authenticated_client):
        """Test deleting a medication"""
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        
        url = reverse('medications:medication-detail', kwargs={'pk': medication.pk})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Medication.objects.count() == 0
    
    def test_filter_medications_by_dosage_form(self, authenticated_client):
        """Test filtering medications by dosage form"""
        Medication.objects.create(
            name='Tablet Med', generic_name='Test1',
            dosage_form='tablet', strength='100mg'
        )
        Medication.objects.create(
            name='Syrup Med', generic_name='Test2',
            dosage_form='syrup', strength='5ml'
        )
        
        url = reverse('medications:medication-list')
        response = authenticated_client.get(url, {'dosage_form': 'tablet'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['dosage_form'] == 'tablet'
    
    def test_search_medications(self, authenticated_client):
        """Test searching medications by name"""
        Medication.objects.create(
            name='Paracetamol', generic_name='Paracetamol',
            dosage_form='tablet', strength='500mg'
        )
        Medication.objects.create(
            name='Ibuprofen', generic_name='Ibuprofen',
            dosage_form='tablet', strength='400mg'
        )
        
        url = reverse('medications:medication-list')
        response = authenticated_client.get(url, {'search': 'para'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Paracetamol' in response.data['results'][0]['name']


@pytest.mark.django_db
class TestPrescriptionAPI:
    """Test suite for Prescription API endpoints"""
    
    def test_list_prescriptions(self, authenticated_client):
        """Test listing prescriptions"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='twice daily',
            frequency_times_per_day=2, duration_days=5
        )
        
        url = reverse('medications:prescription-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_create_prescription(self, authenticated_client):
        """Test creating a prescription"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        
        url = reverse('medications:prescription-list')
        data = {
            'patient': patient.id,
            'medication': medication.id,
            'dosage': '100mg',
            'frequency': 'once daily',
            'frequency_times_per_day': 1,
            'duration_days': 7,
            'route': 'oral'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Prescription.objects.count() == 1
    
    def test_retrieve_prescription(self, authenticated_client):
        """Test retrieving a prescription"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='twice daily',
            frequency_times_per_day=2, duration_days=5
        )
        
        url = reverse('medications:prescription-detail', kwargs={'pk': prescription.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['dosage'] == '100mg'
    
    def test_filter_prescriptions_by_patient(self, authenticated_client):
        """Test filtering prescriptions by patient"""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        Prescription.objects.create(
            patient=patient1, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        Prescription.objects.create(
            patient=patient2, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        url = reverse('medications:prescription-list')
        response = authenticated_client.get(url, {'patient': patient1.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_filter_active_prescriptions(self, authenticated_client):
        """Test filtering active prescriptions"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1,
            duration_days=5, is_active=True
        )
        Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1,
            duration_days=5, is_active=False
        )
        
        url = reverse('medications:prescription-list')
        response = authenticated_client.get(url, {'is_active': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestMedicationAdherenceAPI:
    """Test suite for MedicationAdherence API endpoints"""
    
    def test_list_adherence_records(self, authenticated_client):
        """Test listing adherence records"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='scheduled'
        )
        
        url = reverse('medications:medicationadherence-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_create_adherence_record(self, authenticated_client):
        """Test creating an adherence record"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        
        url = reverse('medications:medicationadherence-list')
        data = {
            'prescription': prescription.id,
            'patient': patient.id,
            'scheduled_time': '08:00:00',
            'status': 'scheduled'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert MedicationAdherence.objects.count() == 1
    
    def test_update_adherence_status(self, authenticated_client):
        """Test updating adherence record status"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        adherence = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='scheduled'
        )
        
        url = reverse('medications:medicationadherence-detail', kwargs={'pk': adherence.pk})
        data = {
            'status': 'taken',
            'taken_at': timezone.now().isoformat()
        }
        
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        adherence.refresh_from_db()
        assert adherence.status == 'taken'
    
    def test_filter_adherence_by_status(self, authenticated_client):
        """Test filtering adherence records by status"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='taken'
        )
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(20, 0), status='scheduled'
        )
        
        url = reverse('medications:medicationadherence-list')
        response = authenticated_client.get(url, {'status': 'taken'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['status'] == 'taken'
    
    def test_filter_adherence_by_patient(self, authenticated_client):
        """Test filtering adherence records by patient"""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription1 = Prescription.objects.create(
            patient=patient1, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        prescription2 = Prescription.objects.create(
            patient=patient2, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=5
        )
        MedicationAdherence.objects.create(
            prescription=prescription1, patient=patient1,
            scheduled_time=time(8, 0), status='scheduled'
        )
        MedicationAdherence.objects.create(
            prescription=prescription2, patient=patient2,
            scheduled_time=time(8, 0), status='scheduled'
        )
        
        url = reverse('medications:medicationadherence-list')
        response = authenticated_client.get(url, {'patient': patient1.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestMedicationCustomActions:
    """Test custom actions for Medication ViewSet"""
    
    def test_active_medications_endpoint(self, authenticated_client):
        """Test the active medications custom endpoint"""
        Medication.objects.create(
            name='Active Med', generic_name='Active',
            dosage_form='tablet', strength='100mg', is_active=True
        )
        Medication.objects.create(
            name='Inactive Med', generic_name='Inactive',
            dosage_form='tablet', strength='100mg', is_active=False
        )
        
        url = reverse('medications:medication-active')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['is_active'] is True


@pytest.mark.django_db
class TestPrescriptionCustomActions:
    """Test custom actions for Prescription ViewSet"""
    
    def test_current_prescriptions_endpoint(self, authenticated_client):
        """Test the current prescriptions custom endpoint"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        today = timezone.now().date()
        
        # Current prescription
        Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1,
            duration_days=7, is_active=True,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=5)
        )
        
        # Expired prescription
        Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1,
            duration_days=7, is_active=True,
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=3)
        )
        
        url = reverse('medications:prescription-current')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestMedicationAdherenceCustomActions:
    """Test custom actions for MedicationAdherence ViewSet"""
    
    def test_mark_taken_action(self, authenticated_client):
        """Test marking an adherence record as taken"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=7
        )
        adherence = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='scheduled'
        )
        
        url = reverse('medications:medicationadherence-mark-taken', args=[adherence.id])
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'taken'
        
        adherence.refresh_from_db()
        assert adherence.status == 'taken'
        assert adherence.taken_at is not None
    
    def test_mark_missed_action(self, authenticated_client):
        """Test marking an adherence record as missed"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=7
        )
        adherence = MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_time=time(8, 0), status='scheduled'
        )
        
        url = reverse('medications:medicationadherence-mark-missed', args=[adherence.id])
        data = {'reason': 'Forgot to take it'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'missed'
        
        adherence.refresh_from_db()
        assert adherence.status == 'missed'
        assert adherence.reason_missed == 'Forgot to take it'
    
    def test_overdue_adherence_endpoint(self, authenticated_client):
        """Test the overdue adherence records endpoint"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=7
        )
        
        # Create past scheduled record (overdue)
        yesterday = (timezone.now() - timedelta(days=1)).date()
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=yesterday,
            scheduled_time=time(8, 0), status='scheduled'
        )
        
        # Create future scheduled record (not overdue)
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        MedicationAdherence.objects.create(
            prescription=prescription, patient=patient,
            scheduled_date=tomorrow,
            scheduled_time=time(8, 0), status='scheduled'
        )
        
        url = reverse('medications:medicationadherence-overdue')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1  # At least the overdue one
    
    def test_adherence_stats_endpoint(self, authenticated_client):
        """Test the adherence statistics endpoint"""
        patient = PatientFactory()
        medication = Medication.objects.create(
            name='Test Med', generic_name='Test',
            dosage_form='tablet', strength='100mg'
        )
        prescription = Prescription.objects.create(
            patient=patient, medication=medication,
            dosage='100mg', frequency='once', frequency_times_per_day=1, duration_days=7
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
            scheduled_time=time(20, 0), status='taken'
        )
        
        url = reverse('medications:medicationadherence-stats')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 3
        assert response.data['taken'] == 2
        assert response.data['missed'] == 1
        assert response.data['adherence_rate'] == 66.67
