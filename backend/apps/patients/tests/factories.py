"""
Test factories for Patient app using factory_boy.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.auth import get_user_model
from apps.patients.models import Patient, Address, EmergencyContact

fake = Faker()
User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    first_name_kinyarwanda = factory.LazyAttribute(lambda obj: obj.first_name)
    last_name_kinyarwanda = factory.LazyAttribute(lambda obj: obj.last_name)

    date_of_birth = factory.Faker("date_of_birth", minimum_age=0, maximum_age=100)
    gender = factory.Iterator(["M", "F"])

    national_id = factory.Sequence(lambda n: f"1{str(n).zfill(15)}")
    phone_number = factory.Sequence(lambda n: f"+2507800{str(n).zfill(5)}")
    email = factory.LazyAttribute(
        lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@example.com"
    )

    blood_type = factory.Iterator(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    is_active = True
    enrolled_by = factory.SubFactory(UserFactory)

    language_preference = "kin"
    prefers_sms = True
    prefers_whatsapp = False


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    patient = factory.SubFactory(PatientFactory)

    province = factory.Iterator(
        ["Kigali", "Eastern", "Northern", "Southern", "Western"]
    )
    district = factory.Faker("city")
    sector = factory.Faker("city_suffix")
    cell = factory.Faker("street_name")
    village = factory.Faker("street_address")

    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")

    street_address = factory.Faker("address")
    landmarks = factory.Faker("sentence")


class EmergencyContactFactory(DjangoModelFactory):
    class Meta:
        model = EmergencyContact

    patient = factory.SubFactory(PatientFactory)
    full_name = factory.Faker("name")
    relationship = factory.Iterator(["parent", "spouse", "sibling", "friend"])
    phone_number = factory.Sequence(lambda n: f"+2507900{str(n).zfill(5)}")
    is_primary = False
