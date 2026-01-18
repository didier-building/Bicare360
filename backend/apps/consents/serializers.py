"""
Serializers for consent management and GDPR compliance.
"""
from rest_framework import serializers
from apps.consents.models import ConsentVersion, Consent, PrivacyPreference, ConsentAuditLog
from apps.patients.serializers import PatientListSerializer


class ConsentVersionSerializer(serializers.ModelSerializer):
    """Serializer for consent versions."""
    
    class Meta:
        model = ConsentVersion
        fields = [
            'id', 'consent_type', 'version_number', 'effective_date',
            'content_english', 'content_kinyarwanda', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ConsentSerializer(serializers.ModelSerializer):
    """Basic serializer for consent records."""
    
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Consent
        fields = [
            'id', 'patient', 'consent_version', 'granted', 'granted_date',
            'revoked_date', 'notes', 'ip_address', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_active']


class ConsentListSerializer(serializers.ModelSerializer):
    """Serializer for consent list views with denormalized data."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    consent_type = serializers.CharField(source='consent_version.consent_type', read_only=True)
    version_number = serializers.CharField(source='consent_version.version_number', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Consent
        fields = [
            'id', 'patient', 'patient_name', 'consent_type', 'version_number',
            'granted', 'granted_date', 'revoked_date', 'is_active'
        ]


class ConsentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for consent with nested relationships."""
    
    patient = PatientListSerializer(read_only=True)
    consent_version = ConsentVersionSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Consent
        fields = [
            'id', 'patient', 'consent_version', 'granted', 'granted_date',
            'revoked_date', 'notes', 'ip_address', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_active']


class ConsentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating consent records."""
    
    class Meta:
        model = Consent
        fields = [
            'patient', 'consent_version', 'granted', 'granted_date',
            'revoked_date', 'notes', 'ip_address'
        ]


class PrivacyPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for patient privacy preferences."""
    
    class Meta:
        model = PrivacyPreference
        fields = [
            'id', 'patient', 'allow_data_export', 'allow_marketing_communications',
            'allow_research_participation', 'allow_third_party_sharing',
            'preferred_contact_method', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ConsentAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for consent audit logs."""
    
    class Meta:
        model = ConsentAuditLog
        fields = [
            'id', 'consent', 'action', 'performed_by', 'timestamp',
            'details', 'ip_address'
        ]
        read_only_fields = ['timestamp']
