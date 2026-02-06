"""
Script to create sample patients for testing.
"""
from django.contrib.auth import get_user_model
from apps.patients.models import Patient
from faker import Faker

fake = Faker()
User = get_user_model()

sample_patients = [
    {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=80),
        'gender': fake.random_element(['M', 'F']),
        'national_id': f"1{fake.random_number(digits=15, fix_len=True)}",
        'phone_number': f"+25078{fake.random_number(digits=7, fix_len=True)}",
        'email': fake.email(),
        'blood_type': fake.random_element(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
    }
    for _ in range(10)
]

for data in sample_patients:
    patient, created = Patient.objects.get_or_create(national_id=data['national_id'], defaults=data)
    if created:
        print(f"Created: {patient}")
    else:
        print(f"Exists: {patient}")
print("\n✅ Sample patients created!")
