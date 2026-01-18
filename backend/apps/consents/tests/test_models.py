"""
Test models for consent management and GDPR compliance.
Following TDD approach - write tests before implementation.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from apps.consents.models import (
    Consent, ConsentVersion, PrivacyPreference, ConsentAuditLog
)
from apps.patients.tests.factories import PatientFactory


@pytest.mark.django_db
class TestConsentVersionModel:
    """Test ConsentVersion model."""
    
    def test_create_consent_version(self):
        """Test creating a consent version with required fields."""
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='We process your data for healthcare purposes.',
            content_kinyarwanda='Tukoresha amakuru yawe mu birebana n\'ubuvuzi.'
        )
        assert version.consent_type == 'data_processing'
        assert version.version_number == '1.0'
        assert version.is_active is True
        assert version.content_english is not None
        
    def test_consent_version_type_choices(self):
        """Test consent version type choices."""
        version = ConsentVersion.objects.create(
            consent_type='marketing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Marketing consent'
        )
        assert version.consent_type in ['data_processing', 'marketing', 'research', 'data_sharing']
        
    def test_consent_version_string_representation(self):
        """Test string representation of consent version."""
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='2.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        assert str(version) == 'data_processing v2.0'
        
    def test_consent_version_ordering(self):
        """Test consent versions are ordered by consent_type and version_number."""
        ConsentVersion.objects.create(
            consent_type='marketing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Marketing v1'
        )
        ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='2.0',
            effective_date=timezone.now().date(),
            content_english='Data v2'
        )
        versions = list(ConsentVersion.objects.all())
        assert versions[0].consent_type == 'data_processing'
        
    def test_consent_version_deactivation(self):
        """Test deactivating a consent version."""
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content',
            is_active=True
        )
        version.is_active = False
        version.save()
        assert version.is_active is False


@pytest.mark.django_db
class TestConsentModel:
    """Test Consent model."""
    
    def test_create_consent_with_required_fields(self):
        """Test creating a consent with required fields."""
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
        assert consent.patient == patient
        assert consent.consent_version == version
        assert consent.granted is True
        assert consent.revoked_date is None
        
    def test_consent_revocation(self):
        """Test revoking a consent."""
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
        revoked_time = timezone.now()
        consent.granted = False
        consent.revoked_date = revoked_time
        consent.save()
        assert consent.granted is False
        assert consent.revoked_date == revoked_time
        
    def test_consent_string_representation(self):
        """Test string representation of consent."""
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
        expected = f"{patient.full_name} - research v1.0 - Granted"
        assert str(consent) == expected
        
    def test_consent_ordering(self):
        """Test consents are ordered by granted_date descending."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        consent1 = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now() - timedelta(days=1)
        )
        consent2 = Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        consents = list(Consent.objects.all())
        assert consents[0].id == consent2.id
        
    def test_consent_patient_cascade_deletion(self):
        """Test that deleting a patient cascades to consents."""
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
        patient_id = patient.id
        patient.delete()
        assert not Consent.objects.filter(patient_id=patient_id).exists()
        
    def test_consent_version_protect_deletion(self):
        """Test that deleting a consent version is protected if consents exist."""
        patient = PatientFactory()
        version = ConsentVersion.objects.create(
            consent_type='data_processing',
            version_number='1.0',
            effective_date=timezone.now().date(),
            content_english='Content'
        )
        Consent.objects.create(
            patient=patient,
            consent_version=version,
            granted=True,
            granted_date=timezone.now()
        )
        with pytest.raises(Exception):  # ProtectedError
            version.delete()
            
    def test_consent_is_active_property(self):
        """Test is_active property returns True if granted and not revoked."""
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
        assert consent.is_active is True
        
        consent.granted = False
        consent.revoked_date = timezone.now()
        consent.save()
        assert consent.is_active is False
        
    def test_consent_optional_fields(self):
        """Test consent with optional fields."""
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
            granted_date=timezone.now(),
            notes='Patient provided verbal consent',
            ip_address='192.168.1.1'
        )
        assert consent.notes is not None
        assert consent.ip_address == '192.168.1.1'


@pytest.mark.django_db
class TestPrivacyPreferenceModel:
    """Test PrivacyPreference model."""
    
    def test_create_privacy_preference(self):
        """Test creating privacy preference with required fields."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            allow_data_export=True,
            allow_marketing_communications=False,
            allow_research_participation=True,
            preferred_contact_method='email'
        )
        assert pref.patient == patient
        assert pref.allow_data_export is True
        assert pref.allow_marketing_communications is False
        
    def test_privacy_preference_contact_method_choices(self):
        """Test privacy preference contact method choices."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            preferred_contact_method='sms'
        )
        assert pref.preferred_contact_method in ['email', 'sms', 'whatsapp', 'phone', 'none']
        
    def test_privacy_preference_string_representation(self):
        """Test string representation of privacy preference."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            preferred_contact_method='email'
        )
        expected = f"Privacy Preferences for {patient.full_name}"
        assert str(pref) == expected
        
    def test_privacy_preference_one_per_patient(self):
        """Test that each patient can have only one privacy preference (unique constraint)."""
        patient = PatientFactory()
        PrivacyPreference.objects.create(
            patient=patient,
            preferred_contact_method='email'
        )
        with pytest.raises(Exception):  # IntegrityError
            PrivacyPreference.objects.create(
                patient=patient,
                preferred_contact_method='sms'
            )
            
    def test_privacy_preference_patient_cascade_deletion(self):
        """Test that deleting a patient cascades to privacy preferences."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            preferred_contact_method='email'
        )
        patient_id = patient.id
        patient.delete()
        assert not PrivacyPreference.objects.filter(patient_id=patient_id).exists()
        
    def test_privacy_preference_default_values(self):
        """Test default values for privacy preferences."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient
        )
        assert pref.allow_data_export is True
        assert pref.allow_marketing_communications is False
        assert pref.allow_research_participation is False
        assert pref.allow_third_party_sharing is False
        assert pref.preferred_contact_method == 'email'
        
    def test_privacy_preference_timestamps(self):
        """Test timestamps are auto-generated."""
        patient = PatientFactory()
        pref = PrivacyPreference.objects.create(
            patient=patient,
            preferred_contact_method='sms'
        )
        assert pref.created_at is not None
        assert pref.updated_at is not None


@pytest.mark.django_db
class TestConsentAuditLogModel:
    """Test ConsentAuditLog model."""
    
    def test_create_audit_log(self):
        """Test creating an audit log entry."""
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
        assert log.consent == consent
        assert log.action == 'granted'
        assert log.performed_by == 'system'
        
    def test_audit_log_action_choices(self):
        """Test audit log action choices."""
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
            action='revoked',
            performed_by='patient'
        )
        assert log.action in ['granted', 'revoked', 'updated', 'viewed', 'exported']
        
    def test_audit_log_string_representation(self):
        """Test string representation of audit log."""
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
        log = ConsentAuditLog.objects.create(
            consent=consent,
            action='granted',
            performed_by='patient'
        )
        assert 'Consent Granted' in str(log) or 'granted' in str(log).lower()
        assert patient.full_name in str(log)
        
    def test_audit_log_ordering(self):
        """Test audit logs are ordered by timestamp descending."""
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
        log1 = ConsentAuditLog.objects.create(
            consent=consent,
            action='granted',
            performed_by='system',
            timestamp=timezone.now() - timedelta(hours=1)
        )
        log2 = ConsentAuditLog.objects.create(
            consent=consent,
            action='viewed',
            performed_by='admin',
            timestamp=timezone.now()
        )
        logs = list(ConsentAuditLog.objects.all())
        assert logs[0].id == log2.id
        
    def test_audit_log_consent_cascade_deletion(self):
        """Test that deleting a consent cascades to audit logs."""
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
            performed_by='system'
        )
        consent_id = consent.id
        consent.delete()
        assert not ConsentAuditLog.objects.filter(consent_id=consent_id).exists()
        
    def test_audit_log_optional_fields(self):
        """Test audit log with optional fields."""
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
            action='updated',
            performed_by='admin',
            details='Updated contact preferences',
            ip_address='10.0.0.1'
        )
        assert log.details is not None
        assert log.ip_address == '10.0.0.1'
        
    def test_audit_log_timestamps(self):
        """Test audit log timestamp is auto-generated."""
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
            performed_by='system'
        )
        assert log.timestamp is not None
