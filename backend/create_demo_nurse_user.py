"""
DEV ONLY: Creates/updates a demo nurse account for local testing.
Do not run in production and do not expose these credentials externally.

Create a demo nurse user with email nurse@test.com and password test123.
"""
from django.contrib.auth.models import User
from apps.nursing.models import NurseProfile

user, created = User.objects.get_or_create(
    username='nurse_demo',
    defaults={
        'first_name': 'Demo',
        'last_name': 'Nurse',
        'email': 'nurse@test.com'
    }
)
if created:
    user.set_password('test123')
    user.save()
    print('Created new user nurse@test.com')
else:
    user.set_password('test123')
    user.save()
    print('Updated password for nurse@test.com')

nurse, created = NurseProfile.objects.get_or_create(
    user=user,
    defaults={
        'license_number': 'RN99999',
        'phone_number': '+250788999999',
        'specialization': 'Demo',
        'current_shift': 'morning',
        'status': 'available',
        'max_concurrent_patients': 8,
        'is_active': True
    }
)
if created:
    print('Created NurseProfile for nurse@test.com')
else:
    print('NurseProfile for nurse@test.com already exists')
print('\n✅ Demo nurse user ready!')
