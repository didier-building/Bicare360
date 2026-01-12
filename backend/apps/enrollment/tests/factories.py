"""
Test factories for enrollment models.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from datetime import date, timedelta
from apps.enrollment.models import Hospital, DischargeSummary
from apps.patients.tests.factories import PatientFactory, UserFactory

fake = Faker()


class HospitalFactory(DjangoModelFactory):
    class Meta:
        model = Hospital
    
    name = factory.Faker("company")
    code = factory.Sequence(lambda n: f"H{n:04d}")
    hospital_type = factory.Faker("random_element", elements=["referral", "district", "health_center", "clinic"])
    province = factory.Faker("random_element", elements=["Kigali", "Eastern", "Northern", "Southern", "Western"])
    district = factory.Faker("random_element", elements=["Gasabo", "Kicukiro", "Nyarugenge", "Rwamagana", "Musanze"])
    sector = "Kimironko"
    phone_number = factory.LazyFunction(lambda: f"+250{fake.numerify(text='#########')}")
    email = factory.Faker("email")
    emr_integration_type = "manual"
    emr_system_name = factory.Faker("random_element", elements=["OpenMRS", "DHIS2", "Manual", ""])
    status = "active"


class DischargeSummaryFactory(DjangoModelFactory):
    class Meta:
        model = DischargeSummary
    
    patient = factory.SubFactory(PatientFactory)
    hospital = factory.SubFactory(HospitalFactory)
    
    admission_date = factory.LazyFunction(lambda: date.today() - timedelta(days=fake.random_int(min=3, max=30)))
    discharge_date = factory.LazyFunction(lambda: date.today() - timedelta(days=fake.random_int(min=0, max=2)))
    
    primary_diagnosis = factory.Faker("random_element", elements=[
        "Hypertension",
        "Type 2 Diabetes Mellitus",
        "Pneumonia",
        "Malaria",
        "Heart Failure",
        "Acute Kidney Injury"
    ])
    secondary_diagnoses = factory.Faker("sentence", nb_words=6)
    
    icd10_primary = factory.Faker("random_element", elements=["I10", "E11", "J18.9", "B54", "I50.9", "N17.9"])
    icd10_secondary = factory.Faker("random_element", elements=["I10, E11", "J18.9, J44.9", "B54", ""])
    
    procedures_performed = factory.Faker("sentence", nb_words=8)
    treatment_summary = factory.Faker("paragraph", nb_sentences=3)
    
    discharge_condition = factory.Faker("random_element", elements=["improved", "stable", "unchanged"])
    
    discharge_instructions = factory.Faker("paragraph", nb_sentences=4)
    discharge_instructions_kinyarwanda = "Mfata umuti wawe buri gihe. Garuka kwa muganga nyuma yibyumweru 2."
    
    diet_instructions = factory.Faker("random_element", elements=[
        "Low salt diet",
        "Diabetic diet - avoid sugar",
        "High protein diet",
        "Normal diet, avoid alcohol",
        ""
    ])
    activity_restrictions = factory.Faker("random_element", elements=[
        "Bed rest for 3 days",
        "Light activity only",
        "No restrictions",
        "Avoid heavy lifting",
        ""
    ])
    
    follow_up_required = True
    follow_up_timeframe = factory.Faker("random_element", elements=["1 week", "2 weeks", "1 month", "3 months"])
    follow_up_with = factory.Faker("random_element", elements=["Cardiology", "General Medicine", "Diabetes Clinic", "Primary Care"])
    
    risk_level = factory.Faker("random_element", elements=["low", "medium", "high"])
    risk_factors = factory.Faker("sentence", nb_words=10)
    
    warning_signs = "Chest pain, difficulty breathing, severe headache, fever above 39°C"
    warning_signs_kinyarwanda = "Ubucuti mu gituza, kuruhuka nabi, umutwe urababaje cyane, umukara urenze 39°C"
    
    attending_physician = factory.Faker("name")
    discharge_nurse = factory.Faker("name")
    
    created_by = factory.SubFactory(UserFactory)
    additional_notes = factory.Faker("sentence", nb_words=10)
