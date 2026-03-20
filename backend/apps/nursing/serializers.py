"""
Serializers for nursing app.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import NurseProfile, PatientAlert, NursePatientAssignment, AlertLog
from apps.patients.serializers import PatientDetailSerializer
from apps.patients.models import Patient
from apps.enrollment.models import DischargeSummary


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class NurseProfileSerializer(serializers.ModelSerializer):
    """Serializer for NurseProfile model."""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    current_patient_count = serializers.ReadOnlyField()
    is_available_for_assignment = serializers.ReadOnlyField()
    
    class Meta:
        model = NurseProfile
        fields = [
            'id', 'user', 'user_id', 'phone_number', 'license_number', 'specialization',
            'current_shift', 'status', 'max_concurrent_patients', 'is_active',
            'current_patient_count', 'is_available_for_assignment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PatientAlertListSerializer(serializers.ModelSerializer):
    """Simplified serializer for alert list views."""
    patient = serializers.SerializerMethodField()
    assigned_nurse = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientAlert
        fields = [
            'id', 'patient', 'alert_type', 'severity', 'title', 'description',
            'status', 'assigned_nurse', 'created_at', 'assigned_at', 
            'acknowledged_at', 'resolved_at', 'sla_deadline', 'is_overdue'
        ]
        read_only_fields = fields
    
    def get_patient(self, obj):
        """Return basic patient info."""
        if not obj.patient:
            return None
        if not obj.patient.user:
            return {
                'id': obj.patient.id,
                'first_name': obj.patient.first_name or 'Unknown',
                'last_name': obj.patient.last_name or 'Patient',
                'medical_record_number': obj.patient.national_id or f'PAT{obj.patient.id}',
            }
        return {
            'id': obj.patient.id,
            'first_name': obj.patient.user.first_name or obj.patient.first_name or 'Unknown',
            'last_name': obj.patient.user.last_name or obj.patient.last_name or 'Patient',
            'medical_record_number': obj.patient.national_id or f'PAT{obj.patient.id}',
        }
    
    def get_assigned_nurse(self, obj):
        """Return basic assigned nurse info."""
        if not obj.assigned_nurse:
            return None
        if not obj.assigned_nurse.user:
            return {
                'id': obj.assigned_nurse.id,
                'user': {
                    'id': 0,
                    'username': 'unknown',
                    'first_name': 'Unknown',
                    'last_name': 'Nurse',
                },
                'phone_number': obj.assigned_nurse.phone_number or '',
                'license_number': obj.assigned_nurse.license_number or '',
            }
        return {
            'id': obj.assigned_nurse.id,
            'user': {
                'id': obj.assigned_nurse.user.id,
                'username': obj.assigned_nurse.user.username or 'unknown',
                'first_name': obj.assigned_nurse.user.first_name or 'Unknown',
                'last_name': obj.assigned_nurse.user.last_name or 'Nurse',
            },
            'phone_number': obj.assigned_nurse.phone_number or '',
            'license_number': obj.assigned_nurse.license_number or '',
        }


class PatientAlertSerializer(serializers.ModelSerializer):
    """Serializer for PatientAlert model."""
    patient = PatientDetailSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
        required=False
    )
    assigned_nurse = NurseProfileSerializer(read_only=True)
    assigned_nurse_id = serializers.PrimaryKeyRelatedField(
        queryset=NurseProfile.objects.all(),
        source='assigned_nurse',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    is_overdue = serializers.ReadOnlyField()
    response_time_minutes = serializers.ReadOnlyField()
    resolution_time_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = PatientAlert
        fields = [
            'id', 'patient', 'patient_id', 'alert_type', 'severity', 'title',
            'description', 'status', 'assigned_nurse', 'assigned_nurse_id',
            'assigned_at', 'created_at', 'acknowledged_at', 'resolved_at',
            'sla_deadline', 'discharge_summary', 'appointment',
            'resolution_notes', 'escalation_reason', 'updated_at',
            'is_overdue', 'response_time_minutes', 'resolution_time_minutes'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'sla_deadline', 'assigned_at',
            'acknowledged_at', 'resolved_at'
        ]


class PatientAlertCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating alerts."""
    
    class Meta:
        model = PatientAlert
        fields = [
            'patient', 'alert_type', 'severity', 'title', 'description',
            'discharge_summary', 'appointment'
        ]


class NursePatientAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for NursePatientAssignment model."""
    nurse = NurseProfileSerializer(read_only=True)
    nurse_id = serializers.PrimaryKeyRelatedField(
        queryset=NurseProfile.objects.all(),
        source='nurse',
        write_only=True
    )
    patient = PatientDetailSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    discharge_summary_id = serializers.PrimaryKeyRelatedField(
        queryset=DischargeSummary.objects.all(),
        source='discharge_summary',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = NursePatientAssignment
        fields = [
            'id', 'nurse', 'nurse_id', 'patient', 'patient_id',
            'discharge_summary', 'discharge_summary_id', 'status', 'priority',
            'assigned_at', 'last_contact_at', 'completed_at', 'notes'
        ]
        read_only_fields = ['assigned_at']


class AlertLogSerializer(serializers.ModelSerializer):
    """Serializer for AlertLog model."""
    performed_by = UserSerializer(read_only=True)
    performed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='performed_by',
        write_only=True,
        required=False
    )
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    
    class Meta:
        model = AlertLog
        fields = [
            'id', 'alert', 'alert_title', 'action', 'performed_by', 'performed_by_id',
            'notes', 'timestamp'
        ]
        read_only_fields = ['timestamp']
