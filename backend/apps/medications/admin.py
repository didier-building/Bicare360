from django.contrib import admin
from .models import (
    Medication, Prescription, MedicationAdherence, PatientMedicationTracker,
    SymptomReport, PrescriptionRefillRequest
)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    """Admin interface for Medication model"""
    
    list_display = [
        'name', 'generic_name', 'dosage_form', 'strength',
        'manufacturer', 'requires_prescription', 'is_active', 'created_at'
    ]
    list_filter = ['dosage_form', 'requires_prescription', 'is_active', 'created_at']
    search_fields = ['name', 'generic_name', 'brand_name', 'manufacturer']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'generic_name', 'brand_name', 'dosage_form', 'strength')
        }),
        ('Manufacturer & Description', {
            'fields': ('manufacturer', 'description')
        }),
        ('Medical Information', {
            'fields': ('indication', 'contraindications', 'side_effects')
        }),
        ('Storage & Requirements', {
            'fields': ('storage_instructions', 'requires_prescription')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """Admin interface for Prescription model"""
    
    list_display = [
        'id', 'patient', 'medication', 'dosage', 'frequency',
        'duration_days', 'is_active', 'start_date', 'end_date', 'created_at'
    ]
    list_filter = ['is_active', 'route', 'created_at', 'start_date']
    search_fields = [
        'patient__first_name', 'patient__last_name',
        'medication__name', 'medication__generic_name',
        'prescribed_by'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'is_current', 'days_remaining']
    autocomplete_fields = ['patient', 'medication']
    
    fieldsets = (
        ('Relationships', {
            'fields': ('discharge_summary', 'patient', 'medication')
        }),
        ('Prescription Details', {
            'fields': (
                'dosage', 'frequency', 'frequency_times_per_day',
                'route', 'duration_days', 'quantity'
            )
        }),
        ('Instructions', {
            'fields': ('instructions', 'instructions_kinyarwanda')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Provider Information', {
            'fields': ('prescribed_by',)
        }),
        ('Refills', {
            'fields': ('refills_allowed', 'refills_remaining')
        }),
        ('Status', {
            'fields': ('is_active', 'is_current', 'days_remaining')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PatientMedicationTracker)
class PatientMedicationTrackerAdmin(admin.ModelAdmin):
    """Admin interface for PatientMedicationTracker model"""
    
    list_display = [
        'id', 'patient', 'medication_name', 'date', 'status', 'taken_time', 'reported_at'
    ]
    list_filter = ['status', 'date', 'reported_at']
    search_fields = [
        'patient__first_name', 'patient__last_name',
        'prescription__medication__name'
    ]
    ordering = ['-date']
    readonly_fields = ['reported_at', 'updated_at']
    autocomplete_fields = ['patient', 'prescription']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Relationships', {
            'fields': ('prescription', 'patient')
        }),
        ('Tracking', {
            'fields': ('date', 'status', 'taken_time')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('reported_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def medication_name(self, obj):
        """Display medication name"""
        return obj.prescription.medication.name if obj.prescription else '-'
    medication_name.short_description = 'Medication'


@admin.register(MedicationAdherence)
class MedicationAdherenceAdmin(admin.ModelAdmin):
    """Admin interface for MedicationAdherence model"""
    
    list_display = [
        'id', 'patient', 'medication_name', 'scheduled_date', 'scheduled_time', 
        'status', 'taken_at', 'reminder_sent'
    ]
    list_filter = ['status', 'scheduled_date', 'reminder_sent', 'created_at']
    search_fields = [
        'patient__first_name', 'patient__last_name',
        'prescription__medication__name'
    ]
    ordering = ['-scheduled_date', '-scheduled_time']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['patient', 'prescription']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Relationships', {
            'fields': ('prescription', 'patient')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time')
        }),
        ('Adherence Tracking', {
            'fields': ('status', 'taken_at')
        }),
        ('Notes', {
            'fields': ('notes', 'reason_missed')
        }),
        ('Reminder', {
            'fields': ('reminder_sent', 'reminder_sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def medication_name(self, obj):
        """Display medication name"""
        return obj.prescription.medication.name if obj.prescription else '-'
    medication_name.short_description = 'Medication'


@admin.register(SymptomReport)
class SymptomReportAdmin(admin.ModelAdmin):
    """Admin interface for SymptomReport model"""
    
    list_display = [
        'id', 'patient', 'title', 'symptom_type', 'severity', 
        'reviewed_by_nurse', 'reported_at'
    ]
    list_filter = ['symptom_type', 'severity', 'reviewed_by_nurse', 'reported_at']
    search_fields = [
        'patient__first_name', 'patient__last_name', 
        'title', 'description'
    ]
    ordering = ['-reported_at']
    readonly_fields = ['reported_at', 'updated_at']
    autocomplete_fields = ['patient', 'related_prescription']
    date_hierarchy = 'reported_at'
    
    fieldsets = (
        ('Patient & Prescription', {
            'fields': ('patient', 'related_prescription')
        }),
        ('Symptom Details', {
            'fields': ('symptom_type', 'title', 'description', 'severity')
        }),
        ('Additional Information', {
            'fields': ('duration', 'trigger')
        }),
        ('Review Status', {
            'fields': ('reviewed_by_nurse', 'nurse_response', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('reported_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PrescriptionRefillRequest)
class PrescriptionRefillRequestAdmin(admin.ModelAdmin):
    """Admin interface for PrescriptionRefillRequest model"""
    
    list_display = [
        'id', 'patient', 'medication_name', 'quantity_requested', 
        'status', 'urgent', 'requested_at'
    ]
    list_filter = ['status', 'urgent', 'requested_at']
    search_fields = [
        'patient__first_name', 'patient__last_name',
        'prescription__medication__name'
    ]
    ordering = ['-requested_at']
    readonly_fields = ['requested_at', 'updated_at']
    autocomplete_fields = ['patient', 'prescription', 'reviewed_by']
    date_hierarchy = 'requested_at'
    
    fieldsets = (
        ('Request Details', {
            'fields': ('patient', 'prescription', 'quantity_requested', 'reason', 'urgent')
        }),
        ('Review', {
            'fields': ('status', 'reviewed_by', 'review_notes', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def medication_name(self, obj):
        """Display medication name"""
        return obj.prescription.medication.name if obj.prescription else '-'
    medication_name.short_description = 'Medication'
