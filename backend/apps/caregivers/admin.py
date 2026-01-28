"""Admin configuration for caregivers app."""
from django.contrib import admin
from apps.caregivers.models import (
    Caregiver, CaregiverService, CaregiverCertification,
    CaregiverBooking, CaregiverReview
)


@admin.register(Caregiver)
class CaregiverAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'profession', 'rating', 'hourly_rate', 'availability_status', 'is_verified']
    list_filter = ['profession', 'availability_status', 'is_verified', 'province']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering = ['-rating', '-created_at']


@admin.register(CaregiverBooking)
class CaregiverBookingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'caregiver', 'service_type', 'start_datetime', 'status', 'total_cost']
    list_filter = ['status', 'service_type']
    search_fields = ['patient__first_name', 'patient__last_name', 'caregiver__first_name']
    ordering = ['-start_datetime']


@admin.register(CaregiverReview)
class CaregiverReviewAdmin(admin.ModelAdmin):
    list_display = ['patient', 'caregiver', 'rating', 'created_at']
    list_filter = ['rating']
    ordering = ['-created_at']
