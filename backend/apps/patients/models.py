"""
Patient models for BiCare 360.
Handles patient enrollment, contact information, and basic demographics.
"""
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class Patient(models.Model):
    """
    Patient model representing individuals enrolled in BiCare 360.
    """

    GENDER_CHOICES = [
        ("M", _("Male")),
        ("F", _("Female")),
        ("O", _("Other")),
    ]

    BLOOD_TYPE_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    first_name_kinyarwanda = models.CharField(max_length=100, blank=True)
    last_name_kinyarwanda = models.CharField(max_length=100, blank=True)

    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # Identifiers
    national_id = models.CharField(
        max_length=16,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{16}$",
                message=_("National ID must be exactly 16 digits"),
            )
        ],
    )

    phone_validator = RegexValidator(
        regex=r"^\+250\d{9}$",
        message=_("Phone number must be in format: +250XXXXXXXXX"),
    )
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    alt_phone_number = models.CharField(
        max_length=13, validators=[phone_validator], blank=True
    )

    email = models.EmailField(blank=True)

    # Medical Information
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)

    # Metadata
    is_active = models.BooleanField(default=True)
    enrolled_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enrolled_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="enrolled_patients",
    )

    # For USSD/SMS Support
    prefers_sms = models.BooleanField(default=True)
    prefers_whatsapp = models.BooleanField(default=False)
    language_preference = models.CharField(
        max_length=10,
        choices=[("kin", _("Kinyarwanda")), ("eng", _("English")), ("fra", _("French"))],
        default="kin",
    )

    class Meta:
        ordering = ["-enrolled_date"]
        indexes = [
            models.Index(fields=["national_id"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["-enrolled_date"]),
        ]
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"

    @property
    def full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """Calculate patient age in years."""
        from datetime import date

        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )


class Address(models.Model):
    """
    Address model for patient location information.
    Based on Rwanda's administrative structure.
    """

    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="address"
    )

    # Rwanda Administrative Structure
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    cell = models.CharField(max_length=50)
    village = models.CharField(max_length=50)

    # GPS Coordinates (for Abafasha field visits)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    # Additional Info
    street_address = models.TextField(blank=True)
    landmarks = models.TextField(blank=True, help_text=_("Nearby landmarks for navigation"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        indexes = [
            models.Index(fields=["province", "district"]),
        ]

    def __str__(self):
        return f"{self.village}, {self.cell}, {self.sector}, {self.district}"


class EmergencyContact(models.Model):
    """
    Emergency contact information for patients.
    """

    RELATIONSHIP_CHOICES = [
        ("parent", _("Parent")),
        ("spouse", _("Spouse")),
        ("child", _("Child")),
        ("sibling", _("Sibling")),
        ("friend", _("Friend")),
        ("other", _("Other")),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="emergency_contacts"
    )

    full_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)

    phone_validator = RegexValidator(
        regex=r"^\+250\d{9}$",
        message=_("Phone number must be in format: +250XXXXXXXXX"),
    )
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    alt_phone_number = models.CharField(
        max_length=13, validators=[phone_validator], blank=True
    )

    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_primary", "full_name"]
        verbose_name = _("Emergency Contact")
        verbose_name_plural = _("Emergency Contacts")

    def __str__(self):
        return f"{self.full_name} ({self.relationship}) - {self.patient.full_name}"
