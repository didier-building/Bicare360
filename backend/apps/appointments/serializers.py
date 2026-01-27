"""
Serializers for appointments app.
"""
from rest_framework import serializers
from django.utils import timezone
from apps.appointments.models import Appointment, AppointmentReminder
from apps.patients.serializers import PatientListSerializer
from apps.enrollment.serializers import HospitalSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    """Basic appointment serializer."""
    
    patient_name = serializers.SerializerMethodField()
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_patient_name(self, obj):
        """Get patient full name."""
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return None


class AppointmentListSerializer(serializers.ModelSerializer):
    """Appointment list serializer with summary data."""
    
    patient_name = serializers.SerializerMethodField()
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'hospital', 'hospital_name',
            'appointment_datetime', 'appointment_type', 'status', 
            'location_type', 'provider_name', 'reason', 'is_upcoming', 'is_overdue'
        ]
    
    def get_patient_name(self, obj):
        """Get patient full name."""
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return None


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
    
    def create(self, validated_data):
        """Create appointment and trigger email notification."""
        print(f"\n🔵 [SERIALIZER CREATE] Starting appointment creation...")
        print(f"   Validated data: {list(validated_data.keys())}")
        
        appointment = Appointment.objects.create(**validated_data)
        
        print(f"   ✅ Appointment {appointment.id} saved to database")
        print(f"   Patient: {appointment.patient.full_name}")
        print(f"   Email: {appointment.patient.email}")
        
        # Send email from serializer as well
        if appointment.patient and appointment.patient.email:
            from apps.messaging.email_service import EmailService
            email_service = EmailService()
            try:
                print(f"   📧 Sending email from serializer...")
                result = email_service.send_appointment_reminder_email(
                    patient_email=appointment.patient.email,
                    patient_name=appointment.patient.full_name,
                    appointment_date=appointment.appointment_datetime.strftime('%B %d, %Y'),
                    appointment_time=appointment.appointment_datetime.strftime('%I:%M %p'),
                    hospital_name=appointment.hospital.name,
                    provider_name=appointment.provider_name or 'Healthcare Provider',
                    appointment_type=appointment.get_appointment_type_display()
                )
                print(f"   ✅ Email sent: {result['recipient']}")
            except Exception as e:
                print(f"   ❌ Email error: {str(e)}")
        
        return appointment


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """Serializer for appointment reminders."""
    
    is_due = serializers.ReadOnlyField()
    
    class Meta:
        model = AppointmentReminder
        fields = '__all__'
        read_only_fields = ('created_at', 'sent_at')


# ============ PATIENT APPOINTMENT MANAGEMENT SERIALIZERS ============

class PatientAppointmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing patient's appointments."""
    
    hospital_name = serializers.CharField(
        source='hospital.name',
        read_only=True
    )
    appointment_type_display = serializers.CharField(
        source='get_appointment_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    location_type_display = serializers.CharField(
        source='get_location_type_display',
        read_only=True
    )
    is_upcoming = serializers.SerializerMethodField()
    days_until_appointment = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'appointment_datetime',
            'appointment_type',
            'appointment_type_display',
            'status',
            'status_display',
            'location_type',
            'location_type_display',
            'provider_name',
            'hospital_name',
            'department',
            'reason',
            'duration_minutes',
            'is_upcoming',
            'days_until_appointment',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_is_upcoming(self, obj):
        """Check if appointment is in the future."""
        return obj.appointment_datetime > timezone.now()
    
    def get_days_until_appointment(self, obj):
        """Calculate days until appointment."""
        if not obj.is_upcoming:
            return None
        delta = (obj.appointment_datetime - timezone.now()).days
        return max(0, delta)


class PatientAppointmentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for patient viewing appointment details."""
    
    hospital_name = serializers.CharField(
        source='hospital.name',
        read_only=True
    )
    hospital_phone = serializers.CharField(
        source='hospital.phone_number',
        read_only=True
    )
    hospital_address = serializers.SerializerMethodField()
    appointment_type_display = serializers.CharField(
        source='get_appointment_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    location_type_display = serializers.CharField(
        source='get_location_type_display',
        read_only=True
    )
    is_upcoming = serializers.SerializerMethodField()
    is_cancellable = serializers.SerializerMethodField()
    is_reschedulable = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'appointment_datetime',
            'appointment_type',
            'appointment_type_display',
            'status',
            'status_display',
            'location_type',
            'location_type_display',
            'provider_name',
            'department',
            'reason',
            'notes',
            'notes_kinyarwanda',
            'duration_minutes',
            'hospital_name',
            'hospital_phone',
            'hospital_address',
            'is_upcoming',
            'is_cancellable',
            'is_reschedulable',
            'cancellation_reason',
            'created_at'
        ]
        read_only_fields = [f for f in fields if f not in ['notes', 'notes_kinyarwanda']]
    
    def get_hospital_address(self, obj):
        """Get hospital address details."""
        if obj.hospital:
            return {
                'province': obj.hospital.province,
                'district': obj.hospital.district,
                'sector': obj.hospital.sector,
            }
        return None
    
    def get_is_upcoming(self, obj):
        """Check if appointment is in the future."""
        return obj.appointment_datetime > timezone.now()
    
    def get_is_cancellable(self, obj):
        """Check if appointment can be cancelled."""
        return (
            obj.is_upcoming and
            obj.status not in ['cancelled', 'completed']
        )
    
    def get_is_reschedulable(self, obj):
        """Check if appointment can be rescheduled."""
        return (
            obj.is_upcoming and
            obj.status not in ['cancelled', 'completed']
        )


class PatientAppointmentRescheduleSerializer(serializers.Serializer):
    """Serializer for rescheduling an appointment."""
    
    appointment_datetime = serializers.DateTimeField(
        required=True,
        help_text='New appointment date and time (must be in the future)'
    )
    
    def validate_appointment_datetime(self, value):
        """Validate that new datetime is in the future."""
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Appointment cannot be scheduled in the past."
            )
        return value


class PatientAppointmentCancelSerializer(serializers.Serializer):
    """Serializer for cancelling an appointment."""
    
    cancellation_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text='Reason for cancellation'
    )
