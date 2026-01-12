"""
Admin configuration for enrollment models.
"""
from django.contrib import admin
from apps.enrollment.models import Hospital, DischargeSummary


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    """Admin for Hospital model."""
    
    list_display = [
        'name', 'code', 'hospital_type', 'province', 'district',
        'status', 'emr_integration_type', 'created_at'
    ]
    list_filter = ['hospital_type', 'province', 'status', 'emr_integration_type']
    search_fields = ['name', 'code', 'district']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'hospital_type', 'status')
        }),
        ('Location', {
            'fields': ('province', 'district', 'sector')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('EMR Integration', {
            'fields': ('emr_integration_type', 'emr_system_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DischargeSummary)
class DischargeSummaryAdmin(admin.ModelAdmin):
    """Admin for DischargeSummary model."""
    
    list_display = [
        'patient', 'hospital', 'discharge_date', 'risk_level',
        'discharge_condition', 'follow_up_required', 'days_since_discharge'
    ]
    list_filter = [
        'risk_level', 'discharge_condition', 'follow_up_required',
        'discharge_date', 'hospital'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name', 'primary_diagnosis',
        'attending_physician'
    ]
    ordering = ['-discharge_date']
    date_hierarchy = 'discharge_date'
    
    fieldsets = (
        ('Patient & Hospital', {
            'fields': ('patient', 'hospital')
        }),
        ('Admission Details', {
            'fields': ('admission_date', 'discharge_date', 'length_of_stay_days')
        }),
        ('Diagnosis & Treatment', {
            'fields': (
                'primary_diagnosis', 'secondary_diagnoses',
                'icd10_primary', 'icd10_secondary',
                'procedures_performed', 'treatment_summary'
            )
        }),
        ('Discharge Information', {
            'fields': (
                'discharge_condition', 'discharge_instructions',
                'discharge_instructions_kinyarwanda', 'diet_instructions',
                'activity_restrictions'
            )
        }),
        ('Follow-up', {
            'fields': (
                'follow_up_required', 'follow_up_timeframe', 'follow_up_with'
            )
        }),
        ('Risk Assessment', {
            'fields': (
                'risk_level', 'risk_factors', 'warning_signs',
                'warning_signs_kinyarwanda'
            )
        }),
        ('Healthcare Providers', {
            'fields': ('attending_physician', 'discharge_nurse')
        }),
        ('Additional Information', {
            'fields': ('additional_notes', 'created_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['length_of_stay_days', 'created_at', 'updated_at']
    
    def days_since_discharge(self, obj):
        """Show days since discharge in list view."""
        return obj.days_since_discharge
    days_since_discharge.short_description = 'Days Since Discharge'
