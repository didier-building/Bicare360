"""
Serializers for enrollment models.
"""
from rest_framework import serializers
from apps.enrollment.models import Hospital, DischargeSummary
from apps.patients.serializers import PatientListSerializer


class HospitalSerializer(serializers.ModelSerializer):
    """Serializer for Hospital model."""
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'code', 'hospital_type', 'province', 'district',
            'sector', 'phone_number', 'email', 'emr_integration_type',
            'emr_system_name', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DischargeSummaryListSerializer(serializers.ModelSerializer):
    """List serializer for DischargeSummary (minimal fields)."""
    
    patient = PatientListSerializer(read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    hospital_code = serializers.CharField(source='hospital.code', read_only=True)
    
    class Meta:
        model = DischargeSummary
        fields = [
            'id', 'patient', 'hospital_name', 'hospital_code',
            'admission_date', 'discharge_date', 'length_of_stay_days',
            'primary_diagnosis', 'discharge_condition', 'risk_level',
            'is_high_risk', 'days_since_discharge', 'follow_up_required'
        ]


class DischargeSummaryDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for DischargeSummary (all fields)."""
    
    patient = PatientListSerializer(read_only=True)
    hospital = HospitalSerializer(read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True,
        default=None
    )
    
    class Meta:
        model = DischargeSummary
        fields = [
            'id', 'patient', 'hospital', 'admission_date', 'discharge_date',
            'length_of_stay_days', 'primary_diagnosis', 'secondary_diagnoses',
            'icd10_primary', 'icd10_secondary', 'procedures_performed',
            'treatment_summary', 'discharge_condition', 'discharge_instructions',
            'discharge_instructions_kinyarwanda', 'diet_instructions',
            'activity_restrictions', 'follow_up_required', 'follow_up_timeframe',
            'follow_up_with', 'risk_level', 'risk_factors', 'warning_signs',
            'warning_signs_kinyarwanda', 'attending_physician', 'discharge_nurse',
            'additional_notes', 'is_high_risk', 'days_since_discharge',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'length_of_stay_days', 'is_high_risk', 'days_since_discharge',
            'created_at', 'updated_at'
        ]


class DischargeSummaryCreateSerializer(serializers.ModelSerializer):
    """Create/Update serializer for DischargeSummary."""
    
    class Meta:
        model = DischargeSummary
        fields = [
            'patient', 'hospital', 'admission_date', 'discharge_date',
            'primary_diagnosis', 'secondary_diagnoses', 'icd10_primary',
            'icd10_secondary', 'procedures_performed', 'treatment_summary',
            'discharge_condition', 'discharge_instructions',
            'discharge_instructions_kinyarwanda', 'diet_instructions',
            'activity_restrictions', 'follow_up_required', 'follow_up_timeframe',
            'follow_up_with', 'risk_level', 'risk_factors', 'warning_signs',
            'warning_signs_kinyarwanda', 'attending_physician', 'discharge_nurse',
            'additional_notes'
        ]
    
    def validate(self, data):
        """Validate discharge summary data."""
        # Validate discharge_date is not before admission_date
        if data.get('discharge_date') and data.get('admission_date'):
            if data['discharge_date'] < data['admission_date']:
                raise serializers.ValidationError({
                    'discharge_date': 'Discharge date cannot be before admission date.'
                })
        
        # Validate follow-up requirements
        if data.get('follow_up_required'):
            if not data.get('follow_up_timeframe'):
                raise serializers.ValidationError({
                    'follow_up_timeframe': 'Follow-up timeframe is required when follow-up is required.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create discharge summary with current user."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
