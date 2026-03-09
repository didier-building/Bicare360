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


class DailyGoal(models.Model):
    """
    Model for patient daily habit goals (Phase 1B - Daily Goals System).
    Tracks recurring daily activities like hydration, exercise, sleep, etc.
    """

    CATEGORY_CHOICES = [
        ("exercise", _("Exercise")),
        ("hydration", _("Hydration")),
        ("medication", _("Medication")),
        ("nutrition", _("Nutrition")),
        ("sleep", _("Sleep")),
        ("meditation", _("Meditation/Mindfulness")),
        ("custom", _("Custom")),
    ]

    DAY_CHOICES = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="daily_goals",
    )

    title = models.CharField(
        max_length=200,
        help_text=_("Goal title (e.g., 'Drink 8 glasses of water')")
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="custom",
    )

    # Targets
    target_value = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Target number to achieve daily (e.g., 8 for 8 glasses)")
    )

    current_value = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Current progress for today")
    )

    # Completion tracking
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Recurrence settings
    is_recurring = models.BooleanField(
        default=True,
        help_text=_("If true, goal repeats on specified days")
    )

    recurrence_days = models.JSONField(
        default=list,
        help_text=_("List of weekday numbers (0=Mon, 6=Sun) when goal is active")
    )

    # Reminder settings
    reminder_time = models.TimeField(
        null=True,
        blank=True,
        help_text=_("Time to send daily reminder (if set)")
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "-created_at"]),
            models.Index(fields=["patient", "is_completed"]),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.title}"

    def tick(self):
        """Mark goal as complete for today."""
        from django.utils import timezone
        if not self.is_completed:
            self.is_completed = True
            self.current_value = self.target_value
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'current_value', 'completed_at', 'updated_at'])

    def untick(self):
        """Mark goal as incomplete."""
        if self.is_completed:
            self.is_completed = False
            self.completed_at = None
            self.save(update_fields=['is_completed', 'completed_at', 'updated_at'])

    def increment(self, amount=1):
        """Increment progress towards goal."""
        self.current_value = min(self.current_value + amount, self.target_value)
        if self.current_value >= self.target_value and not self.is_completed:
            self.tick()
        else:
            self.save(update_fields=['current_value', 'updated_at'])

    @classmethod
    def get_today_goals(cls, patient):
        """Get all active goals for patient for today's weekday."""
        from django.utils import timezone
        import json
        
        today_weekday = timezone.now().weekday()
        
        # Get all recurring goals for this patient
        all_goals = cls.objects.filter(
            patient=patient,
            is_recurring=True
        )
        
        # Filter in Python for SQLite compatibility
        today_goals = []
        for goal in all_goals:
            if not goal.recurrence_days:  # Empty list means all days
                today_goals.append(goal)
            elif today_weekday in goal.recurrence_days:
                today_goals.append(goal)
        
        return today_goals


class GoalProgress(models.Model):
    """
    Historical tracking of daily goal completion.
    Creates a record for each day to track streaks and completion rates.
    """

    goal = models.ForeignKey(
        DailyGoal,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )

    date = models.DateField(help_text=_("Date this progress record is for"))

    completed = models.BooleanField(default=False)

    actual_value = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Actual progress achieved")
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("goal", "date")
        indexes = [
            models.Index(fields=["goal", "-date"]),
            models.Index(fields=["date", "completed"]),
        ]

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.goal.title} - {self.date} {status}"

    @classmethod
    def calculate_streak(cls, goal):
        """Calculate consecutive days of completion for a goal."""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        # Count backwards from today until we find an incomplete day
        while True:
            try:
                progress = cls.objects.get(goal=goal, date=current_date)
                if progress.completed:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            except cls.DoesNotExist:
                break
            
            # Safety limit
            if streak > 365:
                break
        
        return streak

    @classmethod
    def get_completion_rate(cls, goal, days=7):
        """Calculate completion rate over last N days."""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)
        
        progress_records = cls.objects.filter(
            goal=goal,
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_days = progress_records.count()
        if total_days == 0:
            return 0.0
        
        completed_days = progress_records.filter(completed=True).count()
        return round((completed_days / total_days) * 100, 1)
