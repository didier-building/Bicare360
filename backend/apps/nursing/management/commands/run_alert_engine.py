"""
Management command to run the alert engine
"""
from django.core.management.base import BaseCommand
from apps.nursing.alert_engine import AlertEngine


class Command(BaseCommand):
    help = 'Run the alert engine to create alerts for missed medications, appointments, and high-risk discharges'

    def handle(self, *args, **options):
        self.stdout.write('Running alert engine...')
        
        results = AlertEngine.run_all_checks()
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Alert engine completed successfully!"))
        self.stdout.write(f"   Total alerts created: {results['total']}")
        self.stdout.write(f"   - Missed medications: {results['missed_medications']}")
        self.stdout.write(f"   - Missed appointments: {results['missed_appointments']}")
        self.stdout.write(f"   - High-risk discharges: {results['high_risk_discharges']}")
