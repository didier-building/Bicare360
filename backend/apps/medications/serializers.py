from rest_framework import serializers
from apps.medications.models import (
    Medication, Prescription, MedicationAdherence, PatientMedicationTracker,
    SymptomReport, PrescriptionRefillRequest
)
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
    patient_name = serializers.SerializerMethodField()
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'patient_name', 'medication', 'medication_name',
            'dosage', 'frequency', 'frequency_times_per_day', 'route',
            'duration_days', 'start_date', 'end_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'patient_name', 'medication_name', 'created_at']
    
    def get_patient_name(self, obj):
        """Get patient full name."""
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return None


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
    prescription_details = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicationAdherence
        fields = [
            'id', 'prescription', 'prescription_details', 'patient', 'scheduled_date', 'scheduled_time',
            'status', 'taken_at', 'notes', 'reason_missed', 'reminder_sent',
            'reminder_sent_at', 'is_overdue', 'minutes_late', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_overdue', 'minutes_late', 'prescription_details', 'created_at', 'updated_at']
    
    def get_prescription_details(self, obj):
        """Get prescription and patient details for display"""
        if not obj.prescription:
            return None
        
        prescription = obj.prescription
        patient = prescription.patient
        
        return {
            'id': prescription.id,
            'medication_name': prescription.medication.name if prescription.medication else '',
            'dosage': prescription.dosage,
            'frequency': prescription.frequency,
            'frequency_times_per_day': prescription.frequency_times_per_day,
            'patient_id': patient.id if patient else None,
            'patient_name': f"{patient.first_name} {patient.last_name}" if patient else '',
        }


class PatientMedicationTrackerSerializer(serializers.ModelSerializer):
    """Serializer for patient medication tracking"""
    prescription_name = serializers.CharField(source='prescription.medication.name', read_only=True)
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientMedicationTracker
        fields = [
            'id', 'patient', 'patient_name', 'prescription', 'prescription_name',
            'date', 'status', 'taken_time', 'notes', 
            'reported_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient_name', 'prescription_name', 'reported_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else None


class SymptomReportSerializer(serializers.ModelSerializer):
    """Serializer for patient symptom reports"""
    patient_name = serializers.SerializerMethodField()
    prescription_name = serializers.CharField(source='related_prescription.medication.name', read_only=True)
    
    class Meta:
        model = SymptomReport
        fields = [
            'id', 'patient', 'patient_name', 'related_prescription', 'prescription_name',
            'symptom_type', 'title', 'description', 'severity', 'duration', 'trigger',
            'reviewed_by_nurse', 'nurse_response', 'reviewed_at',
            'reported_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'patient_name', 'prescription_name', 
            'reviewed_by_nurse', 'nurse_response', 'reviewed_at',
            'reported_at', 'updated_at'
        ]
    
    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else None


class PrescriptionRefillRequestSerializer(serializers.ModelSerializer):
    """Serializer for prescription refill requests"""
    patient_name = serializers.SerializerMethodField()
    prescription_name = serializers.CharField(source='prescription.medication.name', read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PrescriptionRefillRequest
        fields = [
            'id', 'patient', 'patient_name', 'prescription', 'prescription_name',
            'quantity_requested', 'reason', 'urgent', 'status',
            'reviewed_by', 'reviewed_by_name', 'review_notes', 'reviewed_at',
            'requested_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'patient_name', 'prescription_name', 'reviewed_by_name',
            'reviewed_by', 'review_notes', 'reviewed_at',
            'requested_at', 'updated_at'
        ]
    
    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else None
    
    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}"
        return None
