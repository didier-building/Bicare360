"""
Management command to seed demo health progress data (vitals, goals) for all patients.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from apps.patients.models import Patient
from apps.vitals.models import VitalReading, HealthGoal
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Seed demo health progress data (vitals, goals) for all patients."

    def handle(self, *args, **options):
        fake = Faker()
        User = get_user_model()
        demo_nurse = User.objects.filter(is_staff=True).first()
        if not demo_nurse:
            self.stdout.write(self.style.WARNING('No nurse user found, using None for recorded_by.'))

        vital_types = [
            ("blood_pressure", "mmHg"),
            ("heart_rate", "bpm"),
            ("temperature", "°C"),
            ("weight", "kg"),
            ("oxygen_saturation", "%"),
            ("respiratory_rate", "breaths/min"),
            ("blood_glucose", "mg/dL"),
        ]

        goal_templates = [
            ("Reduce blood pressure", "blood_pressure", 120, "mmHg"),
            ("Maintain healthy weight", "weight", 70, "kg"),
            ("Improve oxygen saturation", "oxygen_saturation", 98, "%"),
        ]

        for patient in Patient.objects.all():
            # Seed vitals (last 30 days)
            for vital_type, unit in vital_types:
                for days_ago in range(0, 30):
                    value = self.generate_vital_value(vital_type)
                    recorded_at = timezone.now() - timezone.timedelta(days=days_ago)
                    VitalReading.objects.create(
                        patient=patient,
                        reading_type=vital_type,
                        value=value,
                        unit=unit,
                        recorded_at=recorded_at,
                        recorded_by=demo_nurse,
                    )
            # Seed goals
            for name, vital_type, target, unit in goal_templates:
                HealthGoal.objects.get_or_create(
                    patient=patient,
                    vital_type=vital_type,
                    goal_name=name,
                    defaults={
                        "target_value": target,
                        "unit": unit,
                        "start_date": timezone.now().date() - timezone.timedelta(days=15),
                        "target_date": timezone.now().date() + timezone.timedelta(days=15),
                        "status": "active",
                        "notes": "Demo goal",
                    },
                )
        self.stdout.write(self.style.SUCCESS('Demo health progress data seeded for all patients.'))

    def generate_vital_value(self, vital_type):
        if vital_type == "blood_pressure":
            return random.randint(110, 140)
        elif vital_type == "heart_rate":
            return random.randint(60, 100)
        elif vital_type == "temperature":
            return round(random.uniform(36.5, 37.5), 1)
        elif vital_type == "weight":
            return random.randint(60, 90)
        elif vital_type == "oxygen_saturation":
            return random.randint(95, 100)
        elif vital_type == "respiratory_rate":
            return random.randint(12, 20)
        elif vital_type == "blood_glucose":
            return random.randint(80, 120)
        return 0
