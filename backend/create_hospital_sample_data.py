"""
Script to create sample hospitals for testing.
"""
from apps.enrollment.models import Hospital

sample_hospitals = [
    {
        'name': 'Kigali University Teaching Hospital',
        'code': 'CHUK',
        'hospital_type': 'referral',
        'province': 'Kigali',
        'district': 'Nyarugenge',
        'sector': 'Muhima',
        'phone_number': '+250788111111',
        'email': 'info@chuk.rw',
        'emr_integration_type': 'api',
        'emr_system_name': 'OpenMRS',
        'status': 'active',
    },
    {
        'name': 'King Faisal Hospital',
        'code': 'KFH',
        'hospital_type': 'referral',
        'province': 'Kigali',
        'district': 'Gasabo',
        'sector': 'Kacyiru',
        'phone_number': '+250788222222',
        'email': 'info@kfh.rw',
        'emr_integration_type': 'hl7',
        'emr_system_name': 'DHIS2',
        'status': 'active',
    },
    {
        'name': 'Butaro District Hospital',
        'code': 'BUTARO',
        'hospital_type': 'district',
        'province': 'Northern',
        'district': 'Burera',
        'sector': 'Butaro',
        'phone_number': '+250788333333',
        'email': 'info@butaro.rw',
        'emr_integration_type': 'manual',
        'emr_system_name': '',
        'status': 'pilot',
    },
    {
        'name': 'Remera Health Center',
        'code': 'REMERA',
        'hospital_type': 'health_center',
        'province': 'Kigali',
        'district': 'Gasabo',
        'sector': 'Remera',
        'phone_number': '+250788444444',
        'email': 'info@remera.rw',
        'emr_integration_type': 'manual',
        'emr_system_name': '',
        'status': 'active',
    },
]

for data in sample_hospitals:
    obj, created = Hospital.objects.get_or_create(code=data['code'], defaults=data)
    if created:
        print(f"Created: {obj}")
    else:
        print(f"Exists: {obj}")
print("\n✅ Sample hospitals created!")
