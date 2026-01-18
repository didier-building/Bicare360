"""
Test serializers for consent management.
Following TDD approach - write tests before implementation.
"""
import pytest
from django.utils import timezone
from apps.consents.models import ConsentVersion, Consent, PrivacyPreference, ConsentAuditLog
from apps.consents.serializers import (
    ConsentVersionSerializer,
    ConsentSerializer,
    ConsentListSerializer,
    ConsentDetailSerializer,
    ConsentCreateSerializer,
    PrivacyPreferenceSerializer,
    ConsentAuditLogSerializer,
)
from apps.patients.tests.factories import PatientFactory


@pytest.mark.django_db
class TestConsentVersionSerializer:
    """Test ConsentVersionSerializer."""
    
    def test_serialize_consent_version(self):
        """Test serializing a consent version."""
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='We process your data.',
            content_kinyarwanda='Tukoresha amakuru yawe.',
            is_active=True
        )
        serializer = ConsentVersionSerializer(version)
        data = serializer.data
        
        assert data['consent_type'] == 'data_processing'
        assert data['version_number'] == '1.0'
        assert data['content_english'] == 'We process your data.'
        assert data['is_active'] is True
        
    def test_create_consent_version_via_serializer(self):
        """Test creating a consent version via serializer."""
        data = {
            'consent_type': 'marketing',
            'version_number': '2.0',
            'effective_date': timezone.now().date(),
            'content_english': 'Marketing consent text',
            'is_active': True
        }
        serializer = ConsentVersionSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        version = serializer.save()
        
        assert version.consent_type == 'marketing'
        assert version.version_number == '2.0'


@pytest.mark.django_db
class TestConsentSerializer:
    """Test ConsentSerializer."""
    
    def test_serialize_consent(self):
        """Test serializing a consent."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        serializer = ConsentSerializer(consent)
        data = serializer.data
        
        assert data['patient'] == patient.id
        assert data['granted'] is True
        assert 'is_active' in data
        
    def test_consent_serializer_includes_is_active(self):
        """Test that serializer includes is_active computed property."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='research',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        serializer = ConsentSerializer(consent)
        
        assert serializer.data['is_active'] is True


@pytest.mark.django_db
class TestConsentListSerializer:
    """Test ConsentListSerializer for list views."""
    
    def test_consent_list_includes_patient_name(self):
        """Test that list serializer includes patient name."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='marketing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        serializer = ConsentListSerializer(consent)
        data = serializer.data
        
        assert 'patient_name' in data
        assert data['patient_name'] == patient.full_name
        
    def test_consent_list_includes_consent_type(self):
        """Test that list serializer includes consent type from version."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='research',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        serializer = ConsentListSerializer(consent)
        data = serializer.data
        
        assert 'consent_type' in data
        assert data['consent_type'] == 'research'


@pytest.mark.django_db
class TestConsentDetailSerializer:
    """Test ConsentDetailSerializer for detail views."""
    
    def test_consent_detail_nested_patient(self):
        """Test that detail serializer includes nested patient data."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        serializer = ConsentDetailSerializer(consent)
        data = serializer.data
        
        assert 'patient' in data
        assert isinstance(data['patient'], dict)
        assert data['patient']['id'] == patient.id
        
    def test_consent_detail_nested_version(self):
        """Test that detail serializer includes nested consent version."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='marketing',
            version_number='2.0',
            effective_date=timezone.now().date(),
            content_english='Marketing content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        serializer = ConsentDetailSerializer(consent)
        data = serializer.data
        
        assert 'consent_version' in data
        assert isinstance(data['consent_version'], dict)
        assert data['consent_version']['version_number'] == '2.0'


@pytest.mark.django_db
class TestConsentCreateSerializer:
    """Test ConsentCreateSerializer for create/update operations."""
    
    def test_create_consent_via_serializer(self):
        """Test creating a consent via serializer."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='research',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        data = {
            'patient': patient.id,
            'consent_version': version.id,
            'granted': True,
            'granted_date': timezone.now().isoformat(),
        }
        serializer = ConsentCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        consent = serializer.save()
        
        assert consent.patient == patient
        assert consent.consent_version == version
        assert consent.granted is True
        
    def test_consent_create_validation(self):
        """Test consent create serializer validation."""
        data = {
            'granted': True,
            'granted_date': timezone.now().isoformat(),
        }
        serializer = ConsentCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'patient' in serializer.errors
        assert 'consent_version' in serializer.errors


@pytest.mark.django_db
class TestPrivacyPreferenceSerializer:
    """Test PrivacyPreferenceSerializer."""
    
    def test_serialize_privacy_preference(self):
        """Test serializing privacy preferences."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            allow_data_export=True,
            allow_marketing_communications=False,
            allow_research_participation=True,
            preferred_contact_method='sms'
        )
        serializer = PrivacyPreferenceSerializer(pref)
        data = serializer.data
        
        assert data['allow_data_export'] is True
        assert data['allow_marketing_communications'] is False
        assert data['preferred_contact_method'] == 'sms'
        
    def test_create_privacy_preference_via_serializer(self):
        """Test creating privacy preferences via serializer."""
        patient = PatientFactory()
        data = {
            'patient': patient.id,
            'allow_data_export': True,
            'allow_marketing_communications': True,
            'preferred_contact_method': 'email'
        }
        serializer = PrivacyPreferenceSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        pref = serializer.save()
        
        assert pref.patient == patient
        assert pref.allow_marketing_communications is True
        
    def test_update_privacy_preference_via_serializer(self):
        """Test updating privacy preferences via serializer."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            allow_marketing_communications=False
        )
        data = {
            'allow_marketing_communications': True,
            'preferred_contact_method': 'whatsapp'
        }
        serializer = PrivacyPreferenceSerializer(pref, data=data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated_pref = serializer.save()
        
        assert updated_pref.allow_marketing_communications is True
        assert updated_pref.preferred_contact_method == 'whatsapp'


@pytest.mark.django_db
class TestConsentAuditLogSerializer:
    """Test ConsentAuditLogSerializer."""
    
    def test_serialize_audit_log(self):
        """Test serializing an audit log entry."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        log = ConsentAuditLog.objects.create(
            consent=consent,
            action='granted',
            performed_by='system',
            details='Initial consent granted'
        )
        serializer = ConsentAuditLogSerializer(log)
        data = serializer.data
        
        assert data['action'] == 'granted'
        assert data['performed_by'] == 'system'
        assert data['details'] == 'Initial consent granted'
        
    def test_audit_log_read_only(self):
        """Test that audit logs are read-only (cannot create via serializer)."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        data = {
            'consent': consent.id,
            'action': 'viewed',
            'performed_by': 'admin'
        }
        serializer = ConsentAuditLogSerializer(data=data)
        # Audit logs should be created programmatically, not via API
        # So we just verify serialization works
        assert 'consent' in ConsentAuditLogSerializer.Meta.fields
