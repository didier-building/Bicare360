"""Serializer tests for nursing app."""
import pytest
from django.contrib.auth.models import User
from apps.nursing.serializers import (
    NurseProfileSerializer, PatientAlertSerializer, 
    NursePatientAssignmentSerializer, AlertLogSerializer
)
from apps.nursing.tests.factories import (
    NurseProfileFactory, PatientAlertFactory,
    NursePatientAssignmentFactory, AlertLogFactory, UserFactory
)
from apps.patients.tests.factories import PatientFactory


@pytest.mark.django_db
class TestNurseProfileSerializer:
    """Test cases for NurseProfileSerializer."""

    def test_serialize_nurse_profile(self):
        """Test serializing a nurse profile."""
        nurse = NurseProfileFactory()
        serializer = NurseProfileSerializer(nurse)
        data = serializer.data
        
        assert data['id'] == nurse.id
        assert data['user']['username'] == nurse.user.username
        assert data['specialization'] == nurse.specialization
        assert data['status'] == nurse.status
        assert data['is_active'] == nurse.is_active

    def test_deserialize_nurse_profile(self):
        """Test deserializing nurse profile data."""
        user = UserFactory()
        data = {
            'user_id': user.id,
            'license_number': 'RN12345',
            'phone_number': '+250788123456',
            'specialization': 'ICU',
            'current_shift': 'morning',
            'status': 'available',
            'is_active': True
        }
        serializer = NurseProfileSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        nurse = serializer.save()
        
        assert nurse.user == user
        assert nurse.license_number == 'RN12345'
        assert nurse.specialization == 'ICU'
        assert nurse.is_active is True


@pytest.mark.django_db
class TestPatientAlertSerializer:
    """Test cases for PatientAlertSerializer."""

    def test_serialize_patient_alert(self):
        """Test serializing a patient alert."""
        alert = PatientAlertFactory()
        serializer = PatientAlertSerializer(alert)
        data = serializer.data
        
        assert data['id'] == alert.id
        assert data['patient']['id'] == alert.patient.id
        assert data['alert_type'] == alert.alert_type
        assert data['severity'] == alert.severity
        assert data['status'] == alert.status

    def test_deserialize_patient_alert(self):
        """Test deserializing patient alert data."""
        patient = PatientFactory()
        nurse = NurseProfileFactory()
        
        data = {
            'patient_id': patient.id,
            'alert_type': 'missed_medication',
            'severity': 'high',
            'title': 'Missed Morning Medication',
            'description': 'High blood pressure medication not taken',
            'assigned_nurse_id': nurse.id
        }
        serializer = PatientAlertSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        alert = serializer.save()
        
        assert alert.patient == patient
        assert alert.alert_type == 'missed_medication'
        assert alert.severity == 'high'
        assert alert.assigned_nurse == nurse

    def test_deserialize_without_nurse(self):
        """Test creating alert without assigned nurse."""
        patient = PatientFactory()
        data = {
            'patient_id': patient.id,
            'alert_type': 'missed_medication',
            'severity': 'medium',
            'title': 'Medication Reminder',
            'description': 'Evening medication reminder'
        }
        serializer = PatientAlertSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        alert = serializer.save()
        
        assert alert.assigned_nurse is None


@pytest.mark.django_db
class TestNursePatientAssignmentSerializer:
    """Test cases for NursePatientAssignmentSerializer."""

    def test_serialize_assignment(self):
        """Test serializing a nurse-patient assignment."""
        assignment = NursePatientAssignmentFactory()
        serializer = NursePatientAssignmentSerializer(assignment)
        data = serializer.data
        
        assert data['id'] == assignment.id
        assert data['nurse']['id'] == assignment.nurse.id
        assert data['patient']['id'] == assignment.patient.id
        assert data['status'] == assignment.status
        assert data['priority'] == assignment.priority

    def test_deserialize_assignment(self):
        """Test deserializing assignment data."""
        from apps.enrollment.tests.factories import DischargeSummaryFactory
        nurse = NurseProfileFactory()
        patient = PatientFactory()
        discharge_summary = DischargeSummaryFactory()
        
        data = {
            'nurse_id': nurse.id,
            'patient_id': patient.id,
            'discharge_summary': discharge_summary.id,
            'status': 'active',
            'priority': 2,
            'notes': 'Requires frequent monitoring'
        }
        serializer = NursePatientAssignmentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assignment = serializer.save()
        
        assert assignment.nurse == nurse
        assert assignment.patient == patient
        assert assignment.status == 'active'
        assert assignment.priority == 2


@pytest.mark.django_db
class TestAlertLogSerializer:
    """Test cases for AlertLogSerializer."""

    def test_serialize_alert_log(self):
        """Test serializing an alert log."""
        log = AlertLogFactory()
        serializer = AlertLogSerializer(log)
        data = serializer.data
        
        assert data['id'] == log.id
        assert data['alert'] == log.alert.id
        assert data['action'] == log.action
        assert data['performed_by']['username'] == log.performed_by.username
        assert 'timestamp' in data

    def test_deserialize_alert_log(self):
        """Test deserializing alert log data."""
        alert = PatientAlertFactory()
        user = UserFactory()
        
        data = {
            'alert': alert.id,
            'action': 'acknowledged',
            'performed_by_id': user.id,
            'notes': 'Alert acknowledged by nurse'
        }
        serializer = AlertLogSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        log = serializer.save()
        
        assert log.alert == alert
        assert log.action == 'acknowledged'
        assert log.performed_by is not None
        assert log.performed_by == user
