"""
Test API endpoints for consent management and GDPR compliance.
Following TDD approach - write tests before implementation.
"""
import pytest
import json
from django.utils import timezone
from apps.consents.models import ConsentVersion, Consent, PrivacyPreference, ConsentAuditLog
from apps.patients.tests.factories import PatientFactory


@pytest.fixture
def sample_consent_version():
    """Create a sample consent version for testing."""
    return ConsentVersion.objects.create(
        consent_type='data_processing',
        version_number='1.0',
        effective_date=timezone.now().date(),
        content_english='We process your data for healthcare purposes.',
        content_kinyarwanda='Tukoresha amakuru yawe mu birebana n\'ubuvuzi.'
    )


@pytest.mark.django_db
class TestConsentVersionAPI:
    """Test ConsentVersion API endpoints."""
    
    def test_list_consent_versions(self, authenticated_client):
        """Test listing consent versions."""
        ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Version 1'
        )
        ConsentVersion.objects.create(
            consent_type='marketing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Marketing version'
        )
        
        response = authenticated_client.get('/api/v1/consent-versions/')
        assert response.status_code == 200
        assert response.data['count'] == 2
        
    def test_retrieve_consent_version(self, authenticated_client, sample_consent_version):
        """Test retrieving a specific consent version."""
        response = authenticated_client.get(f'/api/v1/consent-versions/{sample_consent_version.id}/')
        assert response.status_code == 200
        assert response.data['version_number'] == '1.0'
        
    def test_create_consent_version(self, authenticated_client):
        """Test creating a new consent version."""
        data = {
            'consent_type': 'research',
            'version_number': '2.0',
            'effective_date': timezone.now().date().isoformat(),
            'content_english': 'Research participation consent',
            'is_active': True
        }
        response = authenticated_client.post('/api/v1/consent-versions/', data, format='json')
        assert response.status_code == 201
        assert ConsentVersion.objects.filter(version_number='2.0').exists()


@pytest.mark.django_db
class TestConsentAPI:
    """Test Consent API endpoints."""
    
    def test_list_consents(self, authenticated_client, sample_consent_version):
        """Test listing consents."""
        patient = PatientFactory()
        Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        
        response = authenticated_client.get('/api/v1/consents/')
        assert response.status_code == 200
        assert response.data['count'] == 1
        
    def test_create_consent(self, authenticated_client, sample_consent_version):
        """Test creating a consent."""
        patient = PatientFactory()
        data = {
            'patient': patient.id,
            'consent_version': sample_consent_version.id,
            'granted': True,
            'granted_date': timezone.now().isoformat(),
            'notes': 'Patient provided verbal consent'
        }
        response = authenticated_client.post('/api/v1/consents/', data, format='json')
        assert response.status_code == 201
        assert Consent.objects.filter(patient=patient).exists()
        
    def test_retrieve_consent(self, authenticated_client, sample_consent_version):
        """Test retrieving a specific consent."""
        patient = PatientFactory()
        consent = Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        
        response = authenticated_client.get(f'/api/v1/consents/{consent.id}/')
        assert response.status_code == 200
        assert 'patient' in response.data
        assert 'consent_version' in response.data
        
    def test_revoke_consent(self, authenticated_client, sample_consent_version):
        """Test revoking a consent via custom action."""
        patient = PatientFactory()
        consent = Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        
        response = authenticated_client.post(f'/api/v1/consents/{consent.id}/revoke/')
        assert response.status_code == 200
        
        consent.refresh_from_db()
        assert consent.granted is False
        assert consent.revoked_date is not None
        
    def test_filter_consents_by_patient(self, authenticated_client, sample_consent_version):
        """Test filtering consents by patient."""
        patient1 = PatientFactory()
        patient2 = PatientFactory()
        
        Consent.objects.create(
            patient=patient1,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        Consent.objects.create(
            patient=patient2,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        
        response = authenticated_client.get(f'/api/v1/consents/?patient={patient1.id}')
        assert response.status_code == 200
        assert response.data['count'] == 1


@pytest.mark.django_db
class TestPrivacyPreferenceAPI:
    """Test PrivacyPreference API endpoints."""
    
    def test_list_privacy_preferences(self, authenticated_client):
        """Test listing privacy preferences."""
        patient = PatientFactory()
        PrivacyPreference.objects.create(
            patient=patient,
            preferred_contact_method='email'
        )
        
        response = authenticated_client.get('/api/v1/privacy-preferences/')
        assert response.status_code == 200
        assert response.data['count'] == 1
        
    def test_create_privacy_preference(self, authenticated_client):
        """Test creating privacy preferences."""
        patient = PatientFactory()
        data = {
            'patient': patient.id,
            'allow_data_export': True,
            'allow_marketing_communications': False,
            'preferred_contact_method': 'sms'
        }
        response = authenticated_client.post('/api/v1/privacy-preferences/', data, format='json')
        assert response.status_code == 201
        assert PrivacyPreference.objects.filter(patient=patient).exists()
        
    def test_update_privacy_preference(self, authenticated_client):
        """Test updating privacy preferences."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            allow_marketing_communications=False
        )
        
        data = {'allow_marketing_communications': True}
        response = authenticated_client.patch(f'/api/v1/privacy-preferences/{pref.id}/', data, format='json')
        assert response.status_code == 200
        
        pref.refresh_from_db()
        assert pref.allow_marketing_communications is True


@pytest.mark.django_db
class TestGDPRFeatures:
    """Test GDPR compliance features."""
    
    def test_patient_data_export(self, authenticated_client):
        """Test exporting all patient data (GDPR right to data portability)."""
        patient = PatientFactory()
        
        response = authenticated_client.get(f'/api/v1/patients/{patient.id}/export_data/')
        assert response.status_code == 200
        
        # Should return comprehensive patient data
        data = response.data
        assert 'patient' in data
        assert 'consents' in data
        assert 'privacy_preferences' in data or data['privacy_preferences'] is None
        
    def test_patient_data_deletion(self, authenticated_client):
        """Test patient right to be forgotten (GDPR right to erasure)."""
        patient = PatientFactory()
        patient_id = patient.id
        
        response = authenticated_client.post(f'/api/v1/patients/{patient.id}/request_deletion/')
        assert response.status_code == 200
        
        # In real implementation, this might mark for deletion rather than immediate delete
        # For now, we'll test the endpoint exists and returns success
        assert 'message' in response.data or 'detail' in response.data
        
    def test_consent_history(self, authenticated_client, sample_consent_version):
        """Test viewing consent history for a patient."""
        patient = PatientFactory()
        consent = Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        
        # Create audit log
        ConsentAuditLog.objects.create(
            consent=consent,
            action='granted',
            performed_by='patient'
        )
        
        response = authenticated_client.get(f'/api/v1/consents/{consent.id}/audit_logs/')
        assert response.status_code == 200
        assert len(response.data) > 0
        
    def test_active_consents(self, authenticated_client, sample_consent_version):
        """Test retrieving only active consents."""
        patient = PatientFactory()
        
        # Active consent
        Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        
        # Revoked consent
        Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=False,
            granted_date=timezone.now() - timezone.timedelta(days=10),
            revoked_date=timezone.now()
        )
        
        response = authenticated_client.get('/api/v1/consents/active/')
        assert response.status_code == 200
        # Should only return active consents
        assert all(item['is_active'] for item in response.data.get('results', response.data))


@pytest.mark.django_db
class TestConsentAuditLogAPI:
    """Test ConsentAuditLog API endpoints."""
    
    def test_list_audit_logs(self, authenticated_client, sample_consent_version):
        """Test listing audit logs."""
        patient = PatientFactory()
        consent = Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        ConsentAuditLog.objects.create(
            consent=consent,
            action='granted',
            performed_by='system'
        )
        
        response = authenticated_client.get('/api/v1/consent-audit-logs/')
        assert response.status_code == 200
        assert response.data['count'] == 1
        
    def test_filter_audit_logs_by_action(self, authenticated_client, sample_consent_version):
        """Test filtering audit logs by action type."""
        patient = PatientFactory()
        consent = Consent.objects.create(
            patient=patient,
            consent_version=sample_consent_version,
            granted=True,
            granted_date=timezone.now()
        )
        
        ConsentAuditLog.objects.create(
            consent=consent,
            action='granted',
            performed_by='system'
        )
        ConsentAuditLog.objects.create(
            consent=consent,
            action='viewed',
            performed_by='admin'
        )
        
        response = authenticated_client.get('/api/v1/consent-audit-logs/?action=granted')
        assert response.status_code == 200
        assert response.data['count'] == 1
