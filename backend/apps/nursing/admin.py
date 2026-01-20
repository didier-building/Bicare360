"""
Django admin configuration for nursing app.
"""
from django.contrib import admin
from .models import NurseProfile, PatientAlert, NursePatientAssignment, AlertLog


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'specialization', 'current_shift', 'status', 'is_active']
    list_filter = ['status', 'current_shift', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PatientAlert)
class PatientAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'alert_type', 'severity', 'status', 'assigned_nurse', 'created_at']
    list_filter = ['severity', 'status', 'alert_type']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['created_at', 'updated_at', 'sla_deadline']
    date_hierarchy = 'created_at'


@admin.register(NursePatientAssignment)
class NursePatientAssignmentAdmin(admin.ModelAdmin):
    list_display = ['nurse', 'patient', 'status', 'priority', 'assigned_at']
    list_filter = ['status']
    search_fields = ['nurse__user__first_name', 'nurse__user__last_name', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['assigned_at']


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'action', 'performed_by', 'timestamp']
    list_filter = ['action']
    search_fields = ['alert__title', 'performed_by__username']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
