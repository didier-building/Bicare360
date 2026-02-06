"""
Management command to seed demo patient alerts for the nursing dashboard.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from apps.patients.models import Patient
from apps.nursing.models import PatientAlert, NurseProfile

class Command(BaseCommand):
    help = "Seed demo patient alerts for the nursing dashboard."

    def handle(self, *args, **options):
        fake = Faker()
        nurses = list(NurseProfile.objects.all())
        alert_types = [
            'missed_medication', 'missed_appointment', 'high_risk_discharge',
            'symptom_report', 'readmission_risk', 'medication_side_effect',
            'emergency', 'follow_up_needed'
        ]
        severities = ['low', 'medium', 'high', 'critical']
        statuses = ['new', 'assigned', 'in_progress', 'resolved', 'escalated']

        for patient in Patient.objects.all():
            for _ in range(random.randint(2, 5)):
                alert_type = random.choice(alert_types)
                severity = random.choice(severities)
                status = random.choice(statuses)
                assigned_nurse = random.choice(nurses) if nurses and status in ['assigned', 'in_progress', 'escalated'] else None
                created_at = timezone.now() - timezone.timedelta(days=random.randint(0, 10))
                title = f"{alert_type.replace('_', ' ').title()} for {patient.full_name}"
                description = fake.sentence()
                alert = PatientAlert.objects.create(
                    patient=patient,
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    description=description,
                    status=status,
                    assigned_nurse=assigned_nurse,
                    created_at=created_at,
                )
                # Optionally set resolved_at, acknowledged_at, etc.
                if status == 'resolved':
                    alert.resolved_at = created_at + timezone.timedelta(hours=random.randint(1, 48))
                    alert.acknowledged_at = created_at + timezone.timedelta(hours=1)
                    alert.save()
                elif status in ['assigned', 'in_progress', 'escalated']:
                    alert.acknowledged_at = created_at + timezone.timedelta(hours=1)
                    alert.save()
        self.stdout.write(self.style.SUCCESS('Demo patient alerts seeded for all patients.'))
