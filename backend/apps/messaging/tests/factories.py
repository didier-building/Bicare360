"""Test factories for messaging app using factory_boy."""

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.utils import timezone
from datetime import timedelta
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue
from apps.patients.tests.factories import PatientFactory
from apps.appointments.tests.factories import AppointmentFactory

fake = Faker()


class MessageTemplateFactory(DjangoModelFactory):
    """Factory for creating MessageTemplate instances."""

    class Meta:
        model = MessageTemplate

    name = factory.Sequence(lambda n: f"template_{n}")
    template_type = factory.Iterator(["appointment_reminder", "medication_reminder", "general_notification"])
    message_type = factory.Iterator(["sms", "whatsapp"])
    content_english = factory.Faker("sentence")
    content_kinyarwanda = factory.Faker("sentence")
    is_active = True


class MessageFactory(DjangoModelFactory):
    """Factory for creating Message instances."""

    class Meta:
        model = Message

    recipient_patient = factory.SubFactory(PatientFactory)
    recipient_phone = factory.Sequence(lambda n: f"+2507800{str(n).zfill(5)}")
    message_type = factory.Iterator(["sms", "whatsapp"])
    template = factory.SubFactory(MessageTemplateFactory)
    content = factory.Faker("sentence")
    status = "pending"


class MessageLogFactory(DjangoModelFactory):
    """Factory for creating MessageLog instances."""

    class Meta:
        model = MessageLog

    message = factory.SubFactory(MessageFactory)
    status = factory.Iterator(["sent", "delivered", "failed"])
    provider_message_id = factory.Sequence(lambda n: f"AT-{n}")
    cost = factory.Faker("pydecimal", left_digits=2, right_digits=4, positive=True)
    currency = "USD"


class MessageQueueFactory(DjangoModelFactory):
    """Factory for creating MessageQueue instances."""

    class Meta:
        model = MessageQueue

    recipient_phone = factory.Sequence(lambda n: f"+2507800{str(n).zfill(5)}")
    message_type = factory.Iterator(["sms", "whatsapp"])
    content = factory.Faker("sentence")
    scheduled_time = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=24))
    priority = "normal"
    status = "pending"
