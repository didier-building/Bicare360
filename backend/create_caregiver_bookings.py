"""
Script to create sample caregiver bookings for testing.
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from apps.caregivers.models import Caregiver, CaregiverBooking
from apps.patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

# Get the test caregiver (caregiver_demo user)
caregiver_user = User.objects.filter(username='caregiver_demo').first()
if not caregiver_user:
    print("❌ Caregiver user not found!")
    exit(1)

caregiver = caregiver_user.caregiver_profile
if not caregiver:
    print("❌ Caregiver profile not found!")
    exit(1)

print(f"✓ Found caregiver: {caregiver.full_name}")

# Get available patients
patients = Patient.objects.all()[:3]
if not patients:
    print("❌ No patients found!")
    exit(1)

print(f"✓ Found {patients.count()} patients")

# Create bookings
bookings_created = 0
now = datetime.now()

for i, patient in enumerate(patients):
    start_time = now + timedelta(days=i+1, hours=9)
    end_time = start_time + timedelta(hours=4)
    
    booking = CaregiverBooking.objects.create(
        patient=patient,
        caregiver=caregiver,
        service_type='Home Health Care',
        start_datetime=start_time,
        end_datetime=end_time,
        duration_hours=4,
        location_address="Kigali, Rwanda",
        location_notes=f"Primary care for {patient.full_name}",
        hourly_rate=15.00,
        total_cost=60.00,
        status='confirmed',
        patient_notes='Daily vitals monitoring and medication administration'
    )
    bookings_created += 1
    print(f"✓ Created booking: {patient.full_name} ({booking.id})")

print(f"\n✅ Created {bookings_created} bookings!")

# Verify
final_count = CaregiverBooking.objects.filter(caregiver=caregiver).count()
print(f"Total bookings for {caregiver.full_name}: {final_count}")
