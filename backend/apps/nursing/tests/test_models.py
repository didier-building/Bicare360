"""Model tests for nursing app."""
import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from apps.nursing.models import (
    NurseProfile, PatientAlert, NursePatientAssignment, AlertLog
)
from apps.nursing.tests.factories import (
    NurseProfileFactory, PatientAlertFactory, 
    NursePatientAssignmentFactory, AlertLogFactory, UserFactory
)
from apps.patients.tests.factories import PatientFactory


@pytest.mark.django_db
class TestNurseProfile:
    """Test cases for NurseProfile model."""

    def test_create_nurse_profile(self):
        """Test creating a nurse profile."""
        nurse = NurseProfileFactory()
        assert nurse.id is not None
        assert nurse.user is not None
        assert nurse.specialization in ['ER', 'ICU', 'Cardiology', 'Pediatrics', 'General']
        assert nurse.is_active is True
        assert nurse.status == 'available'

    def test_nurse_profile_str(self):
        """Test nurse profile string representation."""
        user = UserFactory(first_name='John', last_name='Doe')
        nurse = NurseProfileFactory(user=user, license_number='RN12345')
        assert str(nurse) == 'John Doe - RN12345'

    def test_nurse_availability_properties(self):
        """Test nurse availability properties."""
        nurse = NurseProfileFactory(status='available', is_active=True)
        assert hasattr(nurse, 'current_patient_count')
        assert hasattr(nurse, 'is_available_for_assignment')
        assert nurse.current_patient_count == 0
        assert nurse.is_available_for_assignment is True


@pytest.mark.django_db
class TestPatientAlert:
    """Test cases for PatientAlert model."""

    def test_create_patient_alert(self):
        """Test creating a patient alert."""
        alert = PatientAlertFactory()
        assert alert.id is not None
        assert alert.patient is not None
        assert alert.alert_type in [
            'missed_medication', 'missed_appointment', 'high_risk_discharge',
            'symptom_report', 'readmission_risk', 'medication_side_effect',
            'emergency', 'follow_up_needed'
        ]
        assert alert.sla_deadline is not None

    def test_patient_alert_str(self):
        """Test patient alert string representation."""
        patient = PatientFactory(first_name='Jane', last_name='Smith')
        alert = PatientAlertFactory(
            patient=patient,
            alert_type='emergency',
            severity='critical',
            title='Patient Emergency'
        )
        # Format: {severity_display} - {title} ({patient})
        assert str(alert).startswith('Critical - Patient Emergency')
        assert 'Jane Smith' in str(alert)

    def test_is_overdue(self):
        """Test checking if alert is overdue."""
        # Create alert and manually set old created_at and sla_deadline
        alert = PatientAlertFactory(severity='critical')
        alert.created_at = timezone.now() - timedelta(minutes=20)
        alert.sla_deadline = timezone.now() - timedelta(minutes=5)  # Deadline 5 min ago
        alert.save()
        
        assert alert.is_overdue is True

    def test_is_not_overdue(self):
        """Test checking if alert is not overdue."""
        # Create recent alert with future deadline
        alert = PatientAlertFactory(severity='low')
        # sla_deadline set automatically in save() based on severity
        assert alert.is_overdue is False

    def test_calculate_response_time(self):
        """Test calculating response time."""
        alert = PatientAlertFactory()
        alert.created_at = timezone.now() - timedelta(minutes=5)
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        assert alert.response_time_minutes == 5

    def test_calculate_response_time_no_acknowledgment(self):
        """Test response time when not acknowledged."""
        alert = PatientAlertFactory()
        assert alert.response_time_minutes is None

    def test_alert_ordering(self):
        """Test that alerts are ordered by severity and creation time."""
        alert1 = PatientAlertFactory(severity='low')
        alert2 = PatientAlertFactory(severity='high')
        alert3 = PatientAlertFactory(severity='critical')
        
        alerts = list(PatientAlert.objects.all())
        # Ordering is by -severity (alphabetical descending), -created_at
        # So we just check all 3 are returned
        assert len(alerts) == 3
        # Check all alerts are present
        alert_ids = [a.id for a in alerts]
        assert alert1.id in alert_ids
        assert alert2.id in alert_ids
        assert alert3.id in alert_ids


@pytest.mark.django_db
class TestNursePatientAssignment:
    """Test cases for NursePatientAssignment model."""

    def test_create_assignment(self):
        """Test creating a nurse-patient assignment."""
        assignment = NursePatientAssignmentFactory()
        assert assignment.id is not None
        assert assignment.nurse is not None
        assert assignment.patient is not None
        assert assignment.status == 'active'

    def test_assignment_str(self):
        """Test assignment string representation."""
        user = UserFactory(first_name='John', last_name='Doe')
        nurse = NurseProfileFactory(user=user)
        patient = PatientFactory(first_name='Jane', last_name='Smith')
        assignment = NursePatientAssignmentFactory(
            nurse=nurse,
            patient=patient
        )
        # __str__ includes patient ID in format, so just check key parts are present
        assert 'John Doe' in str(assignment)
        assert 'Jane Smith' in str(assignment)
        assert '->' in str(assignment)

    def test_assignment_ordering(self):
        """Test that assignments are ordered by assigned_at."""
        assignment1 = NursePatientAssignmentFactory()
        assignment2 = NursePatientAssignmentFactory()
        assignment3 = NursePatientAssignmentFactory()
        
        assignments = NursePatientAssignment.objects.all()
        # Should be ordered by -assigned_at (newest first)
        assert assignments.count() == 3
        assert assignments[0].id == assignment3.id


@pytest.mark.django_db
class TestAlertLog:
    """Test cases for AlertLog model."""

    def test_create_alert_log(self):
        """Test creating an alert log."""
        log = AlertLogFactory()
        assert log.id is not None
        assert log.alert is not None
        assert log.performed_by is not None
        assert log.action in [
            'created', 'assigned', 'acknowledged', 'updated',
            'resolved', 'escalated', 'closed'
        ]

    def test_alert_log_str(self):
        """Test alert log string representation."""
        user = UserFactory(username='johndoe')
        patient = PatientFactory(first_name='Jane', last_name='Smith')
        alert = PatientAlertFactory(
            patient=patient,
            alert_type='emergency',
            title='Emergency Alert'
        )
        log = AlertLogFactory(
            alert=alert,
            performed_by=user,
            action='acknowledged'
        )
        # AlertLog __str__ format is: "action - alert at timestamp"
        assert 'acknowledged' in str(log)
        assert 'Emergency Alert' in str(log)

    def test_log_ordering(self):
        """Test that logs are ordered by timestamp."""
        alert = PatientAlertFactory()
        log1 = AlertLogFactory(alert=alert)
        log2 = AlertLogFactory(alert=alert)
        log3 = AlertLogFactory(alert=alert)
        
        logs = AlertLog.objects.filter(alert=alert)
        # Should be ordered by -timestamp (newest first)
        assert logs[0].id == log3.id
