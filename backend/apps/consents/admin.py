"""
Django admin configuration for consent management.
"""
from django.contrib import admin
from apps.consents.models import ConsentVersion, Consent, PrivacyPreference, ConsentAuditLog


@admin.register(ConsentVersion)
class ConsentVersionAdmin(admin.ModelAdmin):
    """Admin interface for consent versions."""
    
    list_display = ['consent_type', 'version_number', 'effective_date', 'is_active', 'created_at']
    list_filter = ['consent_type', 'is_active', 'effective_date']
    search_fields = ['consent_type', 'version_number', 'content_english', 'content_kinyarwanda']
    date_hierarchy = 'effective_date'
    ordering = ['consent_type', '-version_number']
    
    fieldsets = (
        ('Version Information', {
            'fields': ('consent_type', 'version_number', 'effective_date', 'is_active')
        }),
        ('Content', {
            'fields': ('content_english', 'content_kinyarwanda')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    """Admin interface for patient consents."""
    
    list_display = ['patient', 'consent_version', 'granted', 'granted_date', 'revoked_date', 'is_active_display']
    list_filter = ['granted', 'granted_date', 'revoked_date', 'consent_version__consent_type']
    search_fields = ['patient__first_name', 'patient__last_name', 'notes']
    autocomplete_fields = ['patient', 'consent_version']
    date_hierarchy = 'granted_date'
    ordering = ['-granted_date']
    
    fieldsets = (
        ('Patient & Consent', {
            'fields': ('patient', 'consent_version')
        }),
        ('Consent Status', {
            'fields': ('granted', 'granted_date', 'revoked_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'ip_address')
        }),
        ('Computed Properties', {
            'fields': ('is_active_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'is_active_display']
    
    def is_active_display(self, obj):
        """Display is_active property."""
        return obj.is_active
    is_active_display.boolean = True
    is_active_display.short_description = 'Active'


@admin.register(PrivacyPreference)
class PrivacyPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for privacy preferences."""
    
    list_display = [
        'patient', 'allow_data_export', 'allow_marketing_communications',
        'allow_research_participation', 'preferred_contact_method', 'updated_at'
    ]
    list_filter = [
        'allow_data_export', 'allow_marketing_communications',
        'allow_research_participation', 'allow_third_party_sharing',
        'preferred_contact_method'
    ]
    search_fields = ['patient__first_name', 'patient__last_name']
    autocomplete_fields = ['patient']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Patient', {
            'fields': ('patient',)
        }),
        ('Data Permissions', {
            'fields': (
                'allow_data_export', 'allow_marketing_communications',
                'allow_research_participation', 'allow_third_party_sharing'
            )
        }),
        ('Contact Preferences', {
            'fields': ('preferred_contact_method',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ConsentAuditLog)
class ConsentAuditLogAdmin(admin.ModelAdmin):
    """Admin interface for consent audit logs."""
    
    list_display = ['consent', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'performed_by', 'timestamp']
    search_fields = ['consent__patient__first_name', 'consent__patient__last_name', 'details']
    autocomplete_fields = ['consent']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Consent & Action', {
            'fields': ('consent', 'action', 'performed_by')
        }),
        ('Details', {
            'fields': ('details', 'ip_address')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
    
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        """Audit logs should only be created programmatically."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Audit logs should be read-only."""
        return False
