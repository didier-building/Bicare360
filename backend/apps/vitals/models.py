"""
Vitals and health progress models for tracking patient health metrics.
"""
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.patients.models import Patient


class VitalReading(models.Model):
    """
    Model for recording patient vital signs at specific points in time.
    Supports blood pressure, heart rate, temperature, weight, oxygen saturation.
    """

    READING_TYPE_CHOICES = [
        ("blood_pressure", _("Blood Pressure")),
        ("heart_rate", _("Heart Rate")),
        ("temperature", _("Temperature")),
        ("weight", _("Weight")),
        ("oxygen_saturation", _("Oxygen Saturation")),
        ("respiratory_rate", _("Respiratory Rate")),
        ("blood_glucose", _("Blood Glucose")),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="vital_readings",
    )

    reading_type = models.CharField(max_length=20, choices=READING_TYPE_CHOICES)
    recorded_at = models.DateTimeField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_vitals",
    )

    # Values stored as floats for flexibility
    value = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text=_("Numeric value of the reading (unit depends on reading type)"),
    )
    
    # Optional second value for readings like blood pressure (systolic/diastolic)
    secondary_value = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Secondary value (e.g., diastolic for blood pressure)"),
    )

    # Unit information
    unit = models.CharField(
        max_length=20,
        help_text=_("Unit of measurement (e.g., bpm, mmHg, °C, kg, %)"),
    )

    # Optional notes
    notes = models.TextField(blank=True, help_text=_("Additional clinical notes"))

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["patient", "-recorded_at"]),
            models.Index(fields=["reading_type", "-recorded_at"]),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.get_reading_type_display()}: {self.value} {self.unit}"


class HealthGoal(models.Model):
    """
    Model for tracking patient health goals (targets for specific vitals).
    """

    STATUS_CHOICES = [
        ("active", _("Active")),
        ("achieved", _("Achieved")),
        ("abandoned", _("Abandoned")),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="health_goals",
    )

    vital_type = models.CharField(
        max_length=20,
        choices=VitalReading.READING_TYPE_CHOICES,
    )

    goal_name = models.CharField(max_length=255, help_text=_("Name of the goal (e.g., 'Reduce blood pressure')"))
    target_value = models.FloatField(
        help_text=_("Target value to achieve"),
    )
    unit = models.CharField(max_length=20, help_text=_("Unit of measurement"))

    start_date = models.DateField()
    target_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient.full_name} - {self.goal_name}"


class HealthTrend(models.Model):
    """
    Pre-calculated health trends for improved API performance.
    Stores aggregated vitals data for time periods.
    """

    TREND_PERIOD_CHOICES = [
        ("daily", _("Daily")),
        ("weekly", _("Weekly")),
        ("monthly", _("Monthly")),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="health_trends",
    )

    vital_type = models.CharField(
        max_length=20,
        choices=VitalReading.READING_TYPE_CHOICES,
    )

    period = models.CharField(max_length=10, choices=TREND_PERIOD_CHOICES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Aggregated values
    reading_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    average_value = models.FloatField(null=True, blank=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    median_value = models.FloatField(null=True, blank=True)

    # For secondary values (e.g., diastolic BP)
    average_secondary_value = models.FloatField(null=True, blank=True)
    min_secondary_value = models.FloatField(null=True, blank=True)
    max_secondary_value = models.FloatField(null=True, blank=True)

    unit = models.CharField(max_length=20)

    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ("improving", _("Improving")),
            ("stable", _("Stable")),
            ("declining", _("Declining")),
        ],
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_end"]
        unique_together = ("patient", "vital_type", "period", "period_start")
        indexes = [
            models.Index(fields=["patient", "vital_type", "-period_end"]),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.vital_type} ({self.period})"
