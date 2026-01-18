from rest_framework import serializers
from apps.medications.models import Medication, Prescription, MedicationAdherence
from apps.patients.serializers import PatientListSerializer
from apps.patients.models import Patient


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication model"""
    
    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'generic_name', 'brand_name', 'dosage_form', 
            'strength', 'manufacturer', 'description', 'indication',
            'contraindications', 'side_effects', 'storage_instructions',
            'requires_prescription', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrescriptionListSerializer(serializers.ModelSerializer):
    """Serializer for listing prescriptions"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'patient_name', 'medication', 'medication_name',
            'dosage', 'frequency', 'frequency_times_per_day', 'route',
            'duration_days', 'start_date', 'end_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'patient_name', 'medication_name', 'created_at']


class PrescriptionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for prescription with nested objects"""
    patient = PatientListSerializer(read_only=True)
    medication = MedicationSerializer(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'discharge_summary', 'patient', 'medication', 'dosage',
            'frequency', 'frequency_times_per_day', 'route', 'duration_days',
            'quantity', 'instructions', 'instructions_kinyarwanda', 'start_date',
            'end_date', 'prescribed_by', 'refills_allowed', 'refills_remaining',
            'is_active', 'is_current', 'days_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_current', 'days_remaining', 'created_at', 'updated_at']


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating prescriptions"""
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'discharge_summary', 'patient', 'medication', 'dosage',
            'frequency', 'frequency_times_per_day', 'route', 'duration_days',
            'quantity', 'instructions', 'instructions_kinyarwanda', 'start_date',
            'end_date', 'prescribed_by', 'refills_allowed', 'refills_remaining',
            'is_active'
        ]
        read_only_fields = ['id']
    
    def validate_frequency_times_per_day(self, value):
        """Ensure frequency times per day is at least 1"""
        if value < 1:
            raise serializers.ValidationError("Frequency times per day must be at least 1")
        return value
    
    def validate_duration_days(self, value):
        """Ensure duration is at least 1 day"""
        if value < 1:
            raise serializers.ValidationError("Duration must be at least 1 day")
        return value


class MedicationAdherenceSerializer(serializers.ModelSerializer):
    """Serializer for medication adherence tracking"""
    is_overdue = serializers.BooleanField(read_only=True)
    minutes_late = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MedicationAdherence
        fields = [
            'id', 'prescription', 'patient', 'scheduled_date', 'scheduled_time',
            'status', 'taken_at', 'notes', 'reason_missed', 'reminder_sent',
            'reminder_sent_at', 'is_overdue', 'minutes_late', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_overdue', 'minutes_late', 'created_at', 'updated_at']
