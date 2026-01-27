"""
Appointment models for scheduling and reminder management.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Appointment(models.Model):
    """
    Appointment model for patient scheduling.
    Supports multiple appointment types and location options.
    """
    
    APPOINTMENT_TYPE_CHOICES = [
        ('follow_up', 'Follow-up Visit'),
        ('medication_review', 'Medication Review'),
        ('consultation', 'Consultation'),
        ('emergency', 'Emergency'),
        ('routine_checkup', 'Routine Checkup'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    LOCATION_TYPE_CHOICES = [
        ('hospital', 'Hospital Visit'),
        ('home_visit', 'Home Visit'),
        ('telemedicine', 'Telemedicine'),
    ]
    
    # Relationships
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text='The patient for this appointment'
    )
    hospital = models.ForeignKey(
        'enrollment.Hospital',
        on_delete=models.PROTECT,
        related_name='appointments',
        help_text='The hospital or facility for this appointment'
    )
    discharge_summary = models.ForeignKey(
        'enrollment.DischargeSummary',
        on_delete=models.SET_NULL,
        related_name='follow_up_appointments',
        null=True,
        blank=True,
        help_text='Related discharge summary if this is a follow-up appointment'
    )
    prescription = models.ForeignKey(
        'medications.Prescription',
        on_delete=models.SET_NULL,
        related_name='review_appointments',
        null=True,
        blank=True,
        help_text='Related prescription if this is a medication review'
    )
    
    # Appointment Details
    appointment_datetime = models.DateTimeField(
        help_text='Date and time of the appointment'
    )
    appointment_type = models.CharField(
        max_length=30,
        choices=APPOINTMENT_TYPE_CHOICES,
        help_text='Type of appointment'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text='Current status of the appointment'
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default='hospital',
        help_text='Where the appointment will take place'
    )
    
    # Provider Information
    provider_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Name of the healthcare provider'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Department or specialty'
    )
    
    # Appointment Details
    reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for the appointment'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes in English'
    )
    notes_kinyarwanda = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes in Kinyarwanda'
    )
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Expected duration in minutes'
    )
    
    # Cancellation tracking
    cancellation_reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for cancellation if appointment was cancelled'
    )
    cancelled_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the appointment was cancelled'
    )
    cancelled_by = models.CharField(
        max_length=50,
        choices=[('patient', 'Patient'), ('nurse', 'Nurse'), ('system', 'System')],
        blank=True,
        null=True,
        help_text='Who cancelled the appointment'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_datetime']
        indexes = [
            models.Index(fields=['appointment_datetime']),
            models.Index(fields=['status']),
            models.Index(fields=['patient', 'appointment_datetime']),
        ]
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.appointment_type} on {self.appointment_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future."""
        return self.appointment_datetime > timezone.now()
    
    @property
    def is_overdue(self):
        """Check if appointment is overdue (past and still scheduled/confirmed)."""
        if self.status not in ['scheduled', 'confirmed']:
            return False
        return self.appointment_datetime < timezone.now()


class AppointmentReminder(models.Model):
    """
    Reminder for appointments.
    Supports SMS, WhatsApp, email, and phone call reminders.
    """
    
    REMINDER_TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('call', 'Phone Call'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders',
        help_text='The appointment this reminder is for'
    )
    
    # Reminder Details
    reminder_datetime = models.DateTimeField(
        help_text='When to send the reminder'
    )
    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_TYPE_CHOICES,
        default='sms',
        help_text='Type of reminder'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Status of the reminder'
    )
    
    # Message
    message = models.TextField(
        blank=True,
        null=True,
        help_text='Custom reminder message in English'
    )
    message_kinyarwanda = models.TextField(
        blank=True,
        null=True,
        help_text='Custom reminder message in Kinyarwanda'
    )
    
    # Delivery Information
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the reminder was actually sent'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text='Error message if sending failed'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['reminder_datetime']
        indexes = [
            models.Index(fields=['reminder_datetime', 'status']),
            models.Index(fields=['appointment']),
        ]
        verbose_name = 'Appointment Reminder'
        verbose_name_plural = 'Appointment Reminders'
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} reminder for {self.appointment} - {self.status}"
    
    @property
    def is_due(self):
        """Check if reminder is due to be sent."""
        if self.status != 'pending':
            return False
        return self.reminder_datetime <= timezone.now()
