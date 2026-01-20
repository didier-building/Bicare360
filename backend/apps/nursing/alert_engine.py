"""
Alert Engine - Automatically creates alerts based on system events
"""
from django.utils import timezone
from datetime import timedelta
from apps.nursing.models import PatientAlert
from apps.medications.models import Prescription, MedicationAdherence
from apps.appointments.models import Appointment
from apps.enrollment.models import DischargeSummary
import logging

logger = logging.getLogger(__name__)


class AlertEngine:
    """Engine for creating patient alerts based on various triggers."""
    
    @staticmethod
    def check_missed_medications():
        """Create alerts for missed medications based on adherence tracking."""
        now = timezone.now()
        # Look for active prescriptions with poor adherence
        
        # Check prescriptions that should be active but may be missed
        active_prescriptions = Prescription.objects.filter(
            is_active=True,
            start_date__lte=now.date(),
            end_date__gte=now.date()
        ).select_related('patient', 'medication')
        
        created_count = 0
        for prescription in active_prescriptions:
            # Check for recent non-adherence records
            recent_adherence = MedicationAdherence.objects.filter(
                prescription=prescription,
                date__gte=now.date() - timedelta(days=3),
                taken=False
            ).count()
            
            # If patient missed doses recently, create alert
            if recent_adherence >= 2:  # Missed 2+ doses in last 3 days
                # Check if alert already exists
                existing = PatientAlert.objects.filter(
                    patient=prescription.patient,
                    alert_type='missed_medication',
                    status__in=['new', 'assigned', 'in_progress'],
                    created_at__gte=now - timedelta(hours=24)
                ).exists()
                
                if not existing:
                    alert = PatientAlert.objects.create(
                        patient=prescription.patient,
                        alert_type='missed_medication',
                        severity='high',
                        title=f'Multiple Missed Doses - {prescription.medication.name}',
                        description=f'Patient has missed {recent_adherence} doses of {prescription.medication.name} in the last 3 days. Prescribed dosage: {prescription.dosage}, {prescription.frequency}.',
                        status='new'
                    )
                    created_count += 1
                    logger.info(f"Created missed medication alert for {alert.patient}: {prescription.medication.name}")
        
        return created_count
    
    @staticmethod
    def check_missed_appointments():
        """Create alerts for missed appointments."""
        now = timezone.now()
        
        # Look for appointments that were scheduled but marked as missed or no-show
        missed_appointments = Appointment.objects.filter(
            status__in=['missed', 'no_show'],
            appointment_datetime__gte=now - timedelta(days=7),  # Only check last 7 days
            appointment_datetime__lt=now
        ).select_related('patient')
        
        created_count = 0
        for appointment in missed_appointments:
            # Check if alert already exists
            existing = PatientAlert.objects.filter(
                patient=appointment.patient,
                alert_type='missed_appointment',
                appointment=appointment,
                status__in=['new', 'assigned', 'in_progress']
            ).exists()
            
            if not existing:
                alert = PatientAlert.objects.create(
                    patient=appointment.patient,
                    alert_type='missed_appointment',
                    severity='medium',
                    title=f'Missed Appointment - {appointment.get_appointment_type_display()}',
                    description=f'Patient missed {appointment.get_appointment_type_display()} appointment scheduled for {appointment.appointment_datetime.strftime("%b %d, %Y at %I:%M %p")}',
                    status='new',
                    appointment=appointment
                )
                created_count += 1
                logger.info(f"Created missed appointment alert for {alert.patient}: {appointment.appointment_type}")
        
        return created_count
    
    @staticmethod
    def check_high_risk_discharges():
        """Create alerts for high-risk discharge patients."""
        # Look for discharge summaries with high risk level
        high_risk_discharges = DischargeSummary.objects.filter(
            risk_level__in=['high', 'very_high'],
            discharge_date__gte=timezone.now() - timedelta(days=30)
        ).select_related('patient')
        
        created_count = 0
        for discharge in high_risk_discharges:
            # Check if alert already exists
            existing = PatientAlert.objects.filter(
                patient=discharge.patient,
                alert_type='high_risk_discharge',
                discharge_summary=discharge,
                status__in=['new', 'assigned', 'in_progress']
            ).exists()
            
            if not existing:
                severity = 'critical' if discharge.risk_level == 'very_high' else 'high'
                alert = PatientAlert.objects.create(
                    patient=discharge.patient,
                    alert_type='high_risk_discharge',
                    severity=severity,
                    title=f'High Readmission Risk - {discharge.primary_diagnosis}',
                    description=f'Patient discharged with {discharge.get_risk_level_display()} risk level. Primary diagnosis: {discharge.primary_diagnosis}. Follow-up required.',
                    status='new',
                    discharge_summary=discharge
                )
                created_count += 1
                logger.info(f"Created high-risk discharge alert for {alert.patient}: {discharge.primary_diagnosis}")
        
        return created_count
    
    @classmethod
    def run_all_checks(cls):
        """Run all alert checks."""
        logger.info("Starting alert engine checks...")
        
        missed_meds = cls.check_missed_medications()
        missed_appts = cls.check_missed_appointments()
        high_risk = cls.check_high_risk_discharges()
        
        total = missed_meds + missed_appts + high_risk
        logger.info(f"Alert engine completed: {total} new alerts created")
        logger.info(f"  - Missed medications: {missed_meds}")
        logger.info(f"  - Missed appointments: {missed_appts}")
        logger.info(f"  - High-risk discharges: {high_risk}")
        
        return {
            'total': total,
            'missed_medications': missed_meds,
            'missed_appointments': missed_appts,
            'high_risk_discharges': high_risk
        }


def run_alert_engine():
    """Standalone function to run alert engine (for Celery tasks)."""
    return AlertEngine.run_all_checks()
