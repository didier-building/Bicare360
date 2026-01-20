"""Factories for nursing app tests."""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from apps.nursing.models import (
    NurseProfile, PatientAlert, NursePatientAssignment, AlertLog
)
from apps.patients.tests.factories import PatientFactory
from apps.enrollment.tests.factories import DischargeSummaryFactory


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'nurse{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class NurseProfileFactory(DjangoModelFactory):
    """Factory for creating NurseProfile instances."""
    class Meta:
        model = NurseProfile

    user = factory.SubFactory(UserFactory)
    phone_number = factory.Faker('phone_number')
    license_number = factory.Sequence(lambda n: f'RN{10000 + n}')
    specialization = factory.Iterator(['ER', 'ICU', 'Cardiology', 'Pediatrics', 'General'])
    current_shift = factory.Iterator(['morning', 'afternoon', 'night'])
    status = 'available'
    max_concurrent_patients = 10
    is_active = True


class PatientAlertFactory(DjangoModelFactory):
    """Factory for creating PatientAlert instances."""
    class Meta:
        model = PatientAlert

    patient = factory.SubFactory(PatientFactory)
    alert_type = factory.Iterator([
        'missed_medication', 'missed_appointment', 'high_risk_discharge',
        'symptom_report', 'readmission_risk', 'medication_side_effect',
        'emergency', 'follow_up_needed'
    ])
    severity = factory.Iterator(['low', 'medium', 'high', 'critical'])
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('sentence')
    status = 'new'
    assigned_nurse = None


class NursePatientAssignmentFactory(DjangoModelFactory):
    """Factory for creating NursePatientAssignment instances."""
    class Meta:
        model = NursePatientAssignment

    nurse = factory.SubFactory(NurseProfileFactory)
    patient = factory.SubFactory(PatientFactory)
    discharge_summary = factory.SubFactory(DischargeSummaryFactory)
    status = 'active'
    priority = factory.Iterator([0, 1, 2, 3])


class AlertLogFactory(DjangoModelFactory):
    """Factory for creating AlertLog instances."""
    class Meta:
        model = AlertLog

    alert = factory.SubFactory(PatientAlertFactory)
    action = factory.Iterator([
        'created', 'assigned', 'acknowledged', 'updated',
        'resolved', 'escalated', 'closed'
    ])
    performed_by = factory.SubFactory(UserFactory)
    notes = factory.Faker('sentence')
