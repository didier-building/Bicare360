"""
Caregiver models for BiCare360.
Manages external caregivers (Abafasha) who provide home care services.
"""
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Caregiver(models.Model):
    """
    Caregiver (Abafasha) profile.
    External care providers who offer home care services to patients.
    """
    
    PROFESSION_CHOICES = [
        ('registered_nurse', 'Registered Nurse'),
        ('licensed_practical_nurse', 'Licensed Practical Nurse'),
        ('certified_nursing_assistant', 'Certified Nursing Assistant'),
        ('home_health_aide', 'Home Health Aide'),
        ('personal_care_aide', 'Personal Care Aide'),
        ('companion', 'Companion Caregiver'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('unavailable', 'Unavailable'),
    ]
    
    # Basic Info
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='caregiver_profile',
        null=True,
        blank=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_validator = RegexValidator(
        regex=r'^\+250\d{9}$',
        message='Phone number must be in format: +250XXXXXXXXX'
    )
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    
    # Professional Info
    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES)
    license_number = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    bio = models.TextField(help_text='Professional bio and experience')
    
    # Location
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50, blank=True)
    
    # Pricing
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Availability
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    
    # Ratings
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    background_check_completed = models.BooleanField(default=False)
    background_check_date = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-created_at']
        indexes = [
            models.Index(fields=['availability_status', 'is_active']),
            models.Index(fields=['province', 'district']),
            models.Index(fields=['-rating']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_profession_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CaregiverService(models.Model):
    """Services offered by caregivers."""
    
    caregiver = models.ForeignKey(
        Caregiver,
        on_delete=models.CASCADE,
        related_name='services'
    )
    service_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['caregiver', 'service_name']
    
    def __str__(self):
        return f"{self.caregiver.full_name} - {self.service_name}"


class CaregiverCertification(models.Model):
    """Certifications and training records."""
    
    caregiver = models.ForeignKey(
        Caregiver,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    certification_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.caregiver.full_name} - {self.certification_name}"


class CaregiverBooking(models.Model):
    """Patient bookings for caregiver services."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='caregiver_bookings'
    )
    caregiver = models.ForeignKey(
        Caregiver,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    # Booking Details
    service_type = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Location
    location_address = models.TextField()
    location_notes = models.TextField(blank=True)
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Notes
    patient_notes = models.TextField(blank=True)
    caregiver_notes = models.TextField(blank=True)
    
    # Cancellation
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.CharField(max_length=20, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['caregiver', 'status']),
            models.Index(fields=['start_datetime']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} → {self.caregiver.full_name} ({self.start_datetime.date()})"


class CaregiverReview(models.Model):
    """Patient reviews for caregivers."""
    
    booking = models.OneToOneField(
        CaregiverBooking,
        on_delete=models.CASCADE,
        related_name='review'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='caregiver_reviews'
    )
    caregiver = models.ForeignKey(
        Caregiver,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # Rating
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Review
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.full_name} → {self.caregiver.full_name} ({self.rating}★)"
