from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.utils import timezone


def get_current_date():
    """Return current date for default value"""
    return timezone.now().date()


class Medication(models.Model):
    """
    Medication catalog for Rwanda healthcare system.
    Stores information about available medications including dosage forms,
    strengths, and prescription requirements.
    """
    
    DOSAGE_FORM_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('patch', 'Patch'),
        ('suppository', 'Suppository'),
    ]
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        help_text='Commercial/brand name of the medication'
    )
    generic_name = models.CharField(
        max_length=200,
        help_text='Generic/scientific name of the medication'
    )
    brand_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Brand name if different from name'
    )
    
    # Dosage Information
    dosage_form = models.CharField(
        max_length=20,
        choices=DOSAGE_FORM_CHOICES,
        help_text='Form of the medication (tablet, syrup, etc.)'
    )
    strength = models.CharField(
        max_length=100,
        help_text='Strength of the medication (e.g., 500mg, 5ml)'
    )
    
    # Manufacturer & Description
    manufacturer = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Manufacturer of the medication'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='General description of the medication'
    )
    
    # Medical Information
    indication = models.TextField(
        blank=True,
        null=True,
        help_text='What the medication is used for'
    )
    contraindications = models.TextField(
        blank=True,
        null=True,
        help_text='When the medication should not be used'
    )
    side_effects = models.TextField(
        blank=True,
        null=True,
        help_text='Common side effects'
    )
    
    # Storage & Requirements
    storage_instructions = models.TextField(
        blank=True,
        null=True,
        help_text='How to store the medication'
    )
    requires_prescription = models.BooleanField(
        default=False,
        help_text='Whether the medication requires a prescription'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the medication is currently available'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'medication'
        verbose_name_plural = 'medications'
    
    def __str__(self):
        return f'{self.name} ({self.strength})'


class Prescription(models.Model):
    """
    Prescription for medications given to patients after discharge.
    Tracks medication details, dosage, frequency, and duration.
    """
    
    ROUTE_CHOICES = [
        ('oral', 'Oral'),
        ('topical', 'Topiucal'),
        ('intravenous', 'Intravenous (IV)'),
        ('intramuscular', 'Intramuscular (IM)'),
        ('subcutaneous', 'Subcutaneous'),
        ('inhalation', 'Inhalation'),
        ('rectal', 'Rectal'),
        ('transdermal', 'Transdermal'),
    ]
    
    # Relationships
    discharge_summary = models.ForeignKey(
        'enrollment.DischargeSummary',
        on_delete=models.CASCADE,
        related_name='prescriptions',
        null=True,
        blank=True,
        help_text='The discharge summary this prescription is associated with'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='prescriptions',
        help_text='The patient this prescription is for'
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name='prescriptions',
        help_text='The prescribed medication'
    )
    
    # Prescription Details
    dosage = models.CharField(
        max_length=100,
        help_text='Dosage amount (e.g., 500mg, 2 tablets, 5ml)'
    )
    frequency = models.CharField(
        max_length=100,
        help_text='How often to take (e.g., twice daily, every 8 hours)'
    )
    frequency_times_per_day = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Number of times per day to take medication'
    )
    route = models.CharField(
        max_length=20,
        choices=ROUTE_CHOICES,
        default='oral',
        help_text='Route of administration'
    )
    duration_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Duration of treatment in days'
    )
    quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Total quantity prescribed'
    )
    
    # Instructions
    instructions = models.TextField(
        blank=True,
        null=True,
        help_text='Special instructions in English (e.g., take with food)'
    )
    instructions_kinyarwanda = models.TextField(
        blank=True,
        null=True,
        help_text='Special instructions in Kinyarwanda'
    )
    
    # Dates
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date to start taking medication'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date to stop taking medication'
    )
    
    # Provider Information
    prescribed_by = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Name of prescribing physician'
    )
    
    # Refills
    refills_allowed = models.PositiveIntegerField(
        default=0,
        help_text='Number of refills allowed'
    )
    refills_remaining = models.PositiveIntegerField(
        default=0,
        help_text='Number of refills remaining'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this prescription is currently active'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'prescription'
        verbose_name_plural = 'prescriptions'
    
    def __str__(self):
        return f'{self.patient.full_name} - {self.medication.name} ({self.dosage}, {self.frequency})'
    
    @property
    def is_current(self):
        """Check if prescription is currently active and within date range"""
        if not self.is_active:
            return False
        
        if self.start_date and self.end_date:
            today = timezone.now().date()
            return self.start_date <= today <= self.end_date
        
        return self.is_active
    
    @property
    def days_remaining(self):
        """Calculate days remaining in prescription"""
        if not self.end_date:
            return None
        
        today = timezone.now().date()
        remaining = (self.end_date - today).days
        return max(0, remaining)


class MedicationAdherence(models.Model):
    """
    Track patient adherence to medication prescriptions.
    Records when medications should be taken and whether they were actually taken.
    """
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('taken', 'Taken'),
        ('missed', 'Missed'),
        ('skipped', 'Skipped'),
        ('late', 'Late'),
    ]
    
    # Relationships
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='adherence_records',
        help_text='The prescription this adherence record is for'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='adherence_records',
        help_text='The patient this adherence record belongs to'
    )
    
    # Scheduling
    scheduled_date = models.DateField(
        default=get_current_date,
        help_text='Date the medication should be taken'
    )
    scheduled_time = models.TimeField(
        help_text='Time the medication should be taken'
    )
    
    # Adherence Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text='Status of this medication dose'
    )
    taken_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the medication was actually taken'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about this dose'
    )
    reason_missed = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Reason why medication was missed or skipped'
    )
    
    # Reminder
    reminder_sent = models.BooleanField(
        default=False,
        help_text='Whether a reminder was sent for this dose'
    )
    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the reminder was sent'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']
        verbose_name = 'medication adherence'
        verbose_name_plural = 'medication adherence records'
        unique_together = ['prescription', 'scheduled_date', 'scheduled_time']
    
    def __str__(self):
        return f'{self.patient.full_name} - {self.prescription.medication.name} - {self.scheduled_date} {self.scheduled_time} ({self.status})'
    
    @property
    def is_overdue(self):
        """Check if this scheduled dose is overdue"""
        if self.status != 'scheduled':
            return False
        
        now = timezone.now()
        scheduled_datetime = timezone.make_aware(
            timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
        )
        return now > scheduled_datetime
    
    @property
    def minutes_late(self):
        """Calculate how many minutes late the medication was taken"""
        if not self.taken_at or self.status != 'late':
            return None
        
        scheduled_datetime = timezone.make_aware(
            timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
        )
        delta = self.taken_at - scheduled_datetime
        return int(delta.total_seconds() / 60)
