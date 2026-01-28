"""Serializers for Caregiver app."""
from rest_framework import serializers
from apps.caregivers.models import (
    Caregiver, CaregiverService, CaregiverCertification,
    CaregiverBooking, CaregiverReview
)


class CaregiverServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaregiverService
        fields = ['id', 'service_name', 'description']


class CaregiverCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaregiverCertification
        fields = ['id', 'certification_name', 'issuing_organization', 'issue_date', 'expiry_date']


class CaregiverListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for caregiver list."""
    services = CaregiverServiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Caregiver
        fields = [
            'id', 'first_name', 'last_name', 'profession', 'experience_years',
            'rating', 'total_reviews', 'hourly_rate', 'province', 'district',
            'availability_status', 'services', 'is_verified'
        ]


class CaregiverDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for caregiver profile."""
    services = CaregiverServiceSerializer(many=True, read_only=True)
    certifications = CaregiverCertificationSerializer(many=True, read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Caregiver
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 'email', 'phone_number',
            'profession', 'license_number', 'experience_years', 'bio',
            'province', 'district', 'sector', 'hourly_rate', 'availability_status',
            'rating', 'total_reviews', 'is_verified', 'background_check_completed',
            'services', 'certifications', 'created_at'
        ]


class CaregiverBookingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    caregiver_name = serializers.CharField(source='caregiver.full_name', read_only=True)
    
    class Meta:
        model = CaregiverBooking
        fields = [
            'id', 'patient', 'patient_name', 'caregiver', 'caregiver_name',
            'service_type', 'start_datetime', 'end_datetime', 'duration_hours',
            'location_address', 'location_notes', 'hourly_rate', 'total_cost',
            'status', 'patient_notes', 'caregiver_notes', 'created_at'
        ]
        read_only_fields = ['total_cost']
    
    def validate(self, data):
        """Calculate total cost."""
        if 'duration_hours' in data and 'hourly_rate' in data:
            data['total_cost'] = data['duration_hours'] * data['hourly_rate']
        return data


class CaregiverReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = CaregiverReview
        fields = [
            'id', 'booking', 'patient', 'patient_name', 'caregiver',
            'rating', 'title', 'comment', 'created_at'
        ]
        read_only_fields = ['patient', 'caregiver']
