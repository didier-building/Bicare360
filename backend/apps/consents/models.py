"""
Consent management models for GDPR compliance.
"""
from django.db import models
from django.utils import timezone


class ConsentVersion(models.Model):
    """
    Consent version model to track different versions of consent text.
    Allows updating consent terms without losing historical data.
    """
    
    CONSENT_TYPE_CHOICES = [
        ('data_processing', 'Data Processing'),
        ('marketing', 'Marketing Communications'),
        ('research', 'Research Participation'),
        ('data_sharing', 'Data Sharing'),
    ]
    
    consent_type = models.CharField(
        max_length=50,
        choices=CONSENT_TYPE_CHOICES,
        help_text='Type of consent'
    )
    version_number = models.CharField(
        max_length=20,
        help_text='Version number (e.g., 1.0, 2.0)'
    )
    effective_date = models.DateField(
        help_text='Date when this version becomes effective'
    )
    content_english = models.TextField(
        help_text='Consent text in English'
    )
    content_kinyarwanda = models.TextField(
        blank=True,
        null=True,
        help_text='Consent text in Kinyarwanda'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this version is currently active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['consent_type', 'version_number']
        unique_together = ['consent_type', 'version_number']
        indexes = [
            models.Index(fields=['consent_type', 'is_active']),
            models.Index(fields=['effective_date']),
        ]
        verbose_name = 'Consent Version'
        verbose_name_plural = 'Consent Versions'
    
    def __str__(self):
        return f"{self.consent_type} v{self.version_number}"


class Consent(models.Model):
    """
    Patient consent tracking model.
    Records when and how patients granted or revoked consent.
    """
    
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='consents',
        help_text='The patient who gave consent'
    )
    consent_version = models.ForeignKey(
        ConsentVersion,
        on_delete=models.PROTECT,
        related_name='consents',
        help_text='The version of consent that was agreed to'
    )
    granted = models.BooleanField(
        default=True,
        help_text='Whether consent is granted or revoked'
    )
    granted_date = models.DateTimeField(
        help_text='When consent was granted'
    )
    revoked_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When consent was revoked (if applicable)'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about the consent'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address from which consent was given'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-granted_date']
        indexes = [
            models.Index(fields=['patient', 'consent_version']),
            models.Index(fields=['granted', 'granted_date']),
        ]
        verbose_name = 'Consent'
        verbose_name_plural = 'Consents'
    
    def __str__(self):
        status = 'Granted' if self.granted else 'Revoked'
        return f"{self.patient.full_name} - {self.consent_version} - {status}"
    
    @property
    def is_active(self):
        """Check if consent is currently active (granted and not revoked)."""
        return self.granted and self.revoked_date is None


class PrivacyPreference(models.Model):
    """
    Patient privacy preferences for GDPR compliance.
    One-to-one relationship with Patient.
    """
    
    CONTACT_METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Phone Call'),
        ('none', 'No Contact'),
    ]
    
    patient = models.OneToOneField(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='privacy_preference',
        help_text='The patient these preferences belong to'
    )
    allow_data_export = models.BooleanField(
        default=True,
        help_text='Allow patient to export their data'
    )
    allow_marketing_communications = models.BooleanField(
        default=False,
        help_text='Allow marketing communications'
    )
    allow_research_participation = models.BooleanField(
        default=False,
        help_text='Allow participation in research studies'
    )
    allow_third_party_sharing = models.BooleanField(
        default=False,
        help_text='Allow sharing data with third parties'
    )
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default='email',
        help_text='Preferred method of contact'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Privacy Preference'
        verbose_name_plural = 'Privacy Preferences'
    
    def __str__(self):
        return f"Privacy Preferences for {self.patient.full_name}"


class ConsentAuditLog(models.Model):
    """
    Audit log for consent changes.
    Tracks all consent-related actions for compliance.
    """
    
    ACTION_CHOICES = [
        ('granted', 'Consent Granted'),
        ('revoked', 'Consent Revoked'),
        ('updated', 'Consent Updated'),
        ('viewed', 'Consent Viewed'),
        ('exported', 'Data Exported'),
    ]
    
    consent = models.ForeignKey(
        Consent,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        help_text='The consent this log entry is for'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='Action performed'
    )
    performed_by = models.CharField(
        max_length=200,
        help_text='Who performed the action (user, system, patient, admin)'
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text='When the action was performed'
    )
    details = models.TextField(
        blank=True,
        null=True,
        help_text='Additional details about the action'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address from which action was performed'
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['consent', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
        verbose_name = 'Consent Audit Log'
        verbose_name_plural = 'Consent Audit Logs'
    
    def __str__(self):
        return f"{self.consent.patient.full_name} - {self.get_action_display()} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
