"""
Models for nurse triage and alert system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class NurseProfile(models.Model):
    """Extended profile for nurses with triage capabilities."""
    
    SHIFT_CHOICES = [
        ('morning', 'Morning (6AM-2PM)'),
        ('afternoon', 'Afternoon (2PM-10PM)'),
        ('night', 'Night (10PM-6AM)'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('on_break', 'On Break'),
        ('off_duty', 'Off Duty'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile')
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100, blank=True)
    current_shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='off_duty')
    max_concurrent_patients = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"
    
    @property
    def current_patient_count(self):
        """Get count of currently assigned patients."""
        return self.patient_assignments.filter(
            status__in=['active', 'pending']
        ).count()
    
    @property
    def is_available_for_assignment(self):
        """Check if nurse can take more patients."""
        return (
            self.is_active and
            self.status == 'available' and
            self.current_patient_count < self.max_concurrent_patients
        )


class PatientAlert(models.Model):
    """Alerts for patient issues requiring nurse attention."""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ALERT_TYPE_CHOICES = [
        ('missed_medication', 'Missed Medication'),
        ('missed_appointment', 'Missed Appointment'),
        ('high_risk_discharge', 'High Risk Discharge'),
        ('symptom_report', 'Symptom Report'),
        ('readmission_risk', 'Readmission Risk'),
        ('medication_side_effect', 'Medication Side Effect'),
        ('emergency', 'Emergency'),
        ('follow_up_needed', 'Follow-up Needed'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]
    
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Assignment tracking
    assigned_nurse = models.ForeignKey(
        'NurseProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # SLA tracking
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    sla_deadline = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    discharge_summary = models.ForeignKey(
        'enrollment.DischargeSummary',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    escalation_reason = models.TextField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity', '-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['assigned_nurse', 'status']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.get_severity_display()} - {self.title} ({self.patient})"
    
    def save(self, *args, **kwargs):
        """Set SLA deadline based on severity."""
        if not self.sla_deadline and not self.pk:
            # Set SLA deadline based on severity
            sla_minutes = {
                'critical': 10,
                'high': 30,
                'medium': 120,
                'low': 240,
            }
            self.sla_deadline = timezone.now() + timedelta(
                minutes=sla_minutes.get(self.severity, 240)
            )
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if alert has exceeded SLA."""
        if self.status in ['resolved', 'closed']:
            return False
        return timezone.now() > self.sla_deadline if self.sla_deadline else False
    
    @property
    def response_time_minutes(self):
        """Calculate response time in minutes."""
        if self.acknowledged_at:
            delta = self.acknowledged_at - self.created_at
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def resolution_time_minutes(self):
        """Calculate resolution time in minutes."""
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return int(delta.total_seconds() / 60)
        return None


class NursePatientAssignment(models.Model):
    """Track nurse assignments to patients."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('transferred', 'Transferred'),
    ]
    
    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.CASCADE,
        related_name='patient_assignments'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='nurse_assignments'
    )
    discharge_summary = models.ForeignKey(
        'enrollment.DischargeSummary',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='nurse_assignments'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=0)  # Higher = more urgent
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    last_contact_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-priority', '-assigned_at']
        indexes = [
            models.Index(fields=['nurse', 'status']),
            models.Index(fields=['patient', 'status']),
        ]
        
    def __str__(self):
        return f"{self.nurse.user.get_full_name()} -> {self.patient}"


class AlertLog(models.Model):
    """Audit log for alert actions."""
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('assigned', 'Assigned'),
        ('acknowledged', 'Acknowledged'),
        ('updated', 'Updated'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]
    
    alert = models.ForeignKey(
        PatientAlert,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alert_actions'
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.action} - {self.alert} at {self.timestamp}"
