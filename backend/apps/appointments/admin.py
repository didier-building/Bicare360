"""
Admin configuration for appointments app.
"""
from django.contrib import admin
from apps.appointments.models import Appointment, AppointmentReminder


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for Appointment model."""
    
    list_display = [
        'id', 'patient', 'hospital', 'appointment_datetime',
        'appointment_type', 'status', 'location_type', 'is_upcoming'
    ]
    list_filter = ['status', 'appointment_type', 'location_type', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'provider_name', 'reason']
    date_hierarchy = 'appointment_datetime'
    readonly_fields = ('is_upcoming', 'is_overdue', 'created_at', 'updated_at')
    autocomplete_fields = ['patient', 'hospital', 'discharge_summary', 'prescription']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'hospital', 'appointment_datetime', 'appointment_type', 'status')
        }),
        ('Location & Provider', {
            'fields': ('location_type', 'provider_name', 'department')
        }),
        ('Details', {
            'fields': ('reason', 'notes', 'notes_kinyarwanda', 'duration_minutes')
        }),
        ('Related Records', {
            'fields': ('discharge_summary', 'prescription'),
            'classes': ('collapse',)
        }),
        ('Computed Properties', {
            'fields': ('is_upcoming', 'is_overdue'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_upcoming(self, obj):
        """Display upcoming status."""
        return obj.is_upcoming
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    """Admin interface for AppointmentReminder model."""
    
    list_display = [
        'id', 'appointment', 'reminder_datetime', 'reminder_type',
        'status', 'is_due', 'sent_at'
    ]
    list_filter = ['status', 'reminder_type', 'created_at']
    search_fields = ['appointment__patient__first_name', 'appointment__patient__last_name']
    date_hierarchy = 'reminder_datetime'
    readonly_fields = ('is_due', 'created_at', 'sent_at')
    autocomplete_fields = ['appointment']
    
    fieldsets = (
        ('Reminder Details', {
            'fields': ('appointment', 'reminder_datetime', 'reminder_type', 'status')
        }),
        ('Messages', {
            'fields': ('message', 'message_kinyarwanda')
        }),
        ('Delivery Information', {
            'fields': ('sent_at', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Computed Properties', {
            'fields': ('is_due',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_due(self, obj):
        """Display due status."""
        return obj.is_due
    is_due.boolean = True
    is_due.short_description = 'Due'
