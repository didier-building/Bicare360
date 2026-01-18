"""Test factories for Appointment app using factory_boy."""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment, AppointmentReminder
from apps.patients.tests.factories import PatientFactory, UserFactory
from apps.enrollment.tests.factories import HospitalFactory

fake = Faker()


class AppointmentFactory(DjangoModelFactory):
    """Factory for creating Appointment instances."""

    class Meta:
        model = Appointment

    patient = factory.SubFactory(PatientFactory)
    hospital = factory.SubFactory(HospitalFactory)
    appointment_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    appointment_type = factory.Iterator(["consultation", "follow_up", "emergency", "routine_checkup"])
    status = "scheduled"
    location_type = "hospital"
    provider_name = factory.Faker("name")
    department = factory.Faker("job")
    duration_minutes = 30
    notes = factory.Faker("sentence")


class AppointmentReminderFactory(DjangoModelFactory):
    """Factory for creating AppointmentReminder instances."""

    class Meta:
        model = AppointmentReminder

    appointment = factory.SubFactory(AppointmentFactory)
    reminder_type = factory.Iterator(["sms", "whatsapp", "email", "call"])
    scheduled_time = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=24))
    status = "pending"
