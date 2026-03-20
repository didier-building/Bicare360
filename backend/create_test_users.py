#!/usr/bin/env python
"""
Create test users for all portal types with known credentials.
Run: python create_test_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from apps.patients.models import Patient
from apps.nursing.models import NurseProfile
from apps.caregivers.models import Caregiver
from datetime import date

User = get_user_model()

def create_test_users():
    """Create test users for all portals."""
    
    print("\n" + "="*80)
    print("Creating Test Users for BiCare360")
    print("="*80)
    
    # 1. PATIENT USER
    print("\n📱 Creating Patient User...")
    patient_user, created = User.objects.get_or_create(
        username='patient1',
        defaults={
            'email': 'patient@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_staff': False,
            'is_superuser': False,
        }
    )
    if created:
        patient_user.set_password('Patient@2026')
        patient_user.save()
        print("✅ Patient user created")
    else:
        patient_user.set_password('Patient@2026')
        patient_user.save()
        print("✅ Patient user password updated")
    
    # Create patient profile
    patient, created = Patient.objects.get_or_create(
        user=patient_user,
        defaults={
            'national_id': '1199012345678901',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'M',
            'phone_number': '+250788123456',
            'is_active': True,
        }
    )
    if created:
        print("✅ Patient profile created")
    else:
        print("✅ Patient profile already exists")
    
    # 2. NURSE/STAFF USER
    print("\n👨‍⚕️ Creating Nurse/Staff User...")
    nurse_user, created = User.objects.get_or_create(
        username='nurse1',
        defaults={
            'email': 'nurse@test.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'is_staff': True,
            'is_superuser': False,
        }
    )
    # Ensure is_staff is True (in case user was created by another script)
    if not nurse_user.is_staff:
        nurse_user.is_staff = True
        nurse_user.save()
        print("✅ Updated nurse user to is_staff=True")
    
    if created:
        nurse_user.set_password('Nurse@2026')
        nurse_user.save()
        print("✅ Nurse user created")
    else:
        nurse_user.set_password('Nurse@2026')
        nurse_user.save()
        print("✅ Nurse user password updated")
    
    # Create nurse profile
    nurse_profile, created = NurseProfile.objects.get_or_create(
        user=nurse_user,
        defaults={
            'license_number': 'RN10001',
            'specialization': 'General Nursing',
            'phone_number': '+250788234567',
            'is_active': True,
        }
    )
    if created:
        print("✅ Nurse profile created")
    else:
        print("✅ Nurse profile already exists")
    
    # 3. CAREGIVER USER
    print("\n🤝 Creating Caregiver User...")
    caregiver_user, created = User.objects.get_or_create(
        username='caregiver1',
        defaults={
            'email': 'caregiver@test.com',
            'first_name': 'Mary',
            'last_name': 'Johnson',
            'is_staff': False,
            'is_superuser': False,
        }
    )
    if created:
        caregiver_user.set_password('Caregiver@2026')
        caregiver_user.save()
        print("✅ Caregiver user created")
    else:
        caregiver_user.set_password('Caregiver@2026')
        caregiver_user.save()
        print("✅ Caregiver user password updated")
    
    # Create caregiver profile
    caregiver, created = Caregiver.objects.get_or_create(
        email='caregiver@test.com',
        defaults={
            'user': caregiver_user,
            'first_name': 'Mary',
            'last_name': 'Johnson',
            'phone_number': '+250788345678',
            'profession': 'registered_nurse',
            'experience_years': 5,
            'bio': 'Experienced professional caregiver with 5+ years experience in home care.',
            'province': 'Kigali',
            'district': 'Gasabo',
            'sector': 'Remera',
            'hourly_rate': 5000,
            'availability_status': 'available',
            'rating': 4.50,
            'is_verified': True,
        }
    )
    if created:
        print("✅ Caregiver profile created")
    else:
        print("✅ Caregiver profile already exists")
    
    # 4. ADMIN USER
    print("\n👑 Creating Admin/Superuser...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@bicare360.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('Admin@2026')
        admin_user.save()
        print("✅ Admin user created")
    else:
        admin_user.set_password('Admin@2026')
        admin_user.save()
        print("✅ Admin user password updated")
    
    # Print credentials
    print("\n" + "="*80)
    print("TEST USER CREDENTIALS")
    print("="*80)
    
    print("\n1. PATIENT PORTAL (http://localhost:5173/patient/login)")
    print("   Login Field: Username or National ID")
    print("   ---")
    print("   Username: patient1")
    print("   Password: Patient@2026")
    print("   (Alternative: National ID: 1199012345678901)")
    print("   Access: Patient Dashboard, My Appointments, Medications, Messages")
    
    print("\n2. STAFF/NURSE PORTAL (http://localhost:5173/login)")
    print("   Login Field: Username")
    print("   ---")
    print("   Username: nurse1")
    print("   Password: Nurse@2026")
    print("   (Alternative: Email: nurse@test.com)")
    print("   Access: Nurse Dashboard, Patient Alerts, Patient Search, Messages")
    
    print("\n3. CAREGIVER PORTAL (http://localhost:5173/caregiver/login)")
    print("   Login Field: Email Address ⚠️")
    print("   ---")
    print("   Email: caregiver@test.com")
    print("   Password: Caregiver@2026")
    print("   ⚠️  IMPORTANT: Must use EMAIL, not username!")
    print("   Access: Caregiver Dashboard, Bookings, Profile, Messages")
    
    print("\n4. ADMIN PORTAL (http://localhost:8000/admin/)")
    print("   Login Field: Username")
    print("   ---")
    print("   Username: admin")
    print("   Password: Admin@2026")
    print("   Access: Full Django Admin Panel")
    
    print("\n" + "="*80)
    print("IMPORTANT NOTES")
    print("="*80)
    print("\n⚠️  CAREGIVER LOGIN:")
    print("   - The caregiver portal login form ONLY accepts EMAIL")
    print("   - Use: caregiver@test.com (NOT caregiver1)")
    print("   - The form validates email format")
    
    print("\n✅ PATIENT & STAFF LOGIN:")
    print("   - Patient portal accepts: username OR national ID")
    print("   - Staff portal accepts: username OR email")
    
    print("\n" + "="*80)
    print("CHAT/MESSAGING ACCESS")
    print("="*80)
    print("\nPatient Messages: http://localhost:5173/patient/messages")
    print("Staff Messages: http://localhost:5173/messages")
    print("Caregiver Messages: http://localhost:5173/caregiver/messages")
    
    print("\n" + "="*80)
    print("✅ All test users created successfully!")
    print("="*80)
    print("\nFor detailed login instructions, see LOGIN_CREDENTIALS_GUIDE.md\n")

if __name__ == '__main__':
    create_test_users()
