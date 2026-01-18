"""
Serializers for appointments app.
"""
from rest_framework import serializers
from apps.appointments.models import Appointment, AppointmentReminder
from apps.patients.serializers import PatientListSerializer
from apps.enrollment.serializers import HospitalSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    """Basic appointment serializer."""
    
    is_upcoming = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment list serializer with summary data."""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'hospital', 'hospital_name',
            'appointment_datetime', 'appointment_type', 'status', 
            'location_type', 'provider_name', 'is_upcoming', 'is_overdue'
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Detailed appointment serializer with nested data."""
    
    patient = PatientListSerializer(read_only=True)
    hospital = HospitalSerializer(read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating appointments."""
    
    class Meta:
        model = Appointment
        fields = [
            'patient', 'hospital', 'discharge_summary', 'prescription',
            'appointment_datetime', 'appointment_type', 'status',
            'location_type', 'provider_name', 'department', 'reason',
            'notes', 'notes_kinyarwanda', 'duration_minutes'
        ]


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """Serializer for appointment reminders."""
    
    is_due = serializers.ReadOnlyField()
    
    class Meta:
        model = AppointmentReminder
        fields = '__all__'
        read_only_fields = ('created_at', 'sent_at')
