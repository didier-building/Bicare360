"""
Models for enrollment and discharge management.
Handles hospital registration and discharge summaries.
"""
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from apps.patients.models import Patient

User = get_user_model()


class Hospital(models.Model):
    """Hospital or health facility."""
    
    name = models.CharField(max_length=200)
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique hospital code (e.g., CHUK, KFH)"
    )
    hospital_type = models.CharField(
        max_length=50,
        choices=[
            ('referral', 'Referral Hospital'),
            ('district', 'District Hospital'),
            ('health_center', 'Health Center'),
            ('clinic', 'Clinic'),
        ],
        default='district'
    )
    
    # Location
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50, blank=True)
    
    # Contact
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+250\d{9}$',
                message="Phone number must be in format: +250XXXXXXXXX"
            )
        ]
    )
    email = models.EmailField(blank=True)
    
    # Integration
    emr_integration_type = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Entry'),
            ('api', 'API Integration'),
            ('hl7', 'HL7 Integration'),
        ],
        default='manual'
    )
    emr_system_name = models.CharField(max_length=100, blank=True, help_text="e.g., OpenMRS, DHIS2")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('pilot', 'Pilot Program'),
            ('inactive', 'Inactive'),
        ],
        default='active'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitals"
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class DischargeSummary(models.Model):
    """
    Comprehensive discharge summary capturing all information 
    needed for post-discharge care coordination.
    """
    
    # Core Relationships
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='discharge_summaries'
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name='discharge_summaries'
    )
    
    # Admission & Discharge Dates
    admission_date = models.DateField()
    discharge_date = models.DateField()
    length_of_stay_days = models.PositiveIntegerField(editable=False)
    
    # Medical Information
    primary_diagnosis = models.TextField(
        help_text="Main diagnosis for admission"
    )
    secondary_diagnoses = models.TextField(
        blank=True,
        help_text="Additional diagnoses (comma-separated or free text)"
    )
    
    # ICD-10 Codes (optional but useful for analytics)
    icd10_primary = models.CharField(max_length=10, blank=True)
    icd10_secondary = models.CharField(max_length=200, blank=True)
    
    # Treatment Summary
    procedures_performed = models.TextField(
        blank=True,
        help_text="Surgeries, procedures, interventions performed"
    )
    treatment_summary = models.TextField(
        help_text="Overview of treatment provided during stay"
    )
    
    # Discharge Information
    discharge_condition = models.CharField(
        max_length=50,
        choices=[
            ('improved', 'Improved'),
            ('stable', 'Stable'),
            ('unchanged', 'Unchanged'),
            ('deteriorated', 'Deteriorated'),
        ],
        default='improved'
    )
    
    discharge_instructions = models.TextField(
        help_text="Instructions for patient and family in patient's language"
    )
    discharge_instructions_kinyarwanda = models.TextField(blank=True)
    
    diet_instructions = models.TextField(
        blank=True,
        help_text="Special dietary requirements or restrictions"
    )
    activity_restrictions = models.TextField(
        blank=True,
        help_text="Physical activity limitations"
    )
    
    # Follow-up Requirements
    follow_up_required = models.BooleanField(default=True)
    follow_up_timeframe = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., '1 week', '2 weeks', '1 month'"
    )
    follow_up_with = models.CharField(
        max_length=200,
        blank=True,
        help_text="Which department or specialist"
    )
    
    # Risk Assessment
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
            ('critical', 'Critical'),
        ],
        default='medium',
        help_text="Risk of readmission or complications"
    )
    
    risk_factors = models.TextField(
        blank=True,
        help_text="Specific risk factors identified (e.g., social determinants, compliance concerns)"
    )
    
    # Warning Signs
    warning_signs = models.TextField(
        blank=True,
        help_text="Symptoms that should prompt immediate medical attention"
    )
    warning_signs_kinyarwanda = models.TextField(blank=True)
    
    # Provider Information
    attending_physician = models.CharField(max_length=200)
    discharge_nurse = models.CharField(max_length=200, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_discharge_summaries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes
    additional_notes = models.TextField(
        blank=True,
        help_text="Any other relevant information"
    )
    
    class Meta:
        ordering = ['-discharge_date', '-created_at']
        verbose_name = "Discharge Summary"
        verbose_name_plural = "Discharge Summaries"
        indexes = [
            models.Index(fields=['patient', 'discharge_date']),
            models.Index(fields=['hospital', 'discharge_date']),
            models.Index(fields=['risk_level']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.hospital.code} - {self.discharge_date}"
    
    def save(self, *args, **kwargs):
        """Calculate length of stay automatically."""
        if self.admission_date and self.discharge_date:
            self.length_of_stay_days = (self.discharge_date - self.admission_date).days
        super().save(*args, **kwargs)
    
    @property
    def is_high_risk(self):
        """Check if patient is high risk."""
        return self.risk_level in ['high', 'critical']
    
    @property
    def days_since_discharge(self):
        """Calculate days since discharge."""
        from django.utils import timezone
        return (timezone.now().date() - self.discharge_date).days
