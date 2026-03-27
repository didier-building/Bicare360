"""
DEV ONLY: Creates patient/nurse demo chat data for local testing.
Do not run in production and do not expose demo credentials externally.

Create Patient-Nurse Chat Demo Data

Creates sample patient and nurse users with a conversation for testing the chat feature.
Use this instead of create_chat_demo_data.py since caregivers don't have a portal yet.

Usage:
    python create_patient_nurse_chat_demo.py

Demo Users Created:
    - Patient: patient@test.com / test123
    - Nurse: nurse@test.com / test123

Author: Didier IMANIRAHARI
Date: March 2026
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from apps.patients.models import Patient
from apps.nursing.models import NurseProfile
from apps.chat.models import Conversation, ChatMessage

User = get_user_model()

def create_demo_data():
    """Create demo users, conversations, and messages."""
    
    print("🚀 Creating patient-nurse chat demo data...\n")
    
    # Create patient user
    print("👤 Creating patient user...")
    patient_user, created = User.objects.get_or_create(
        username='patient_demo',
        defaults={
            'email': 'patient@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }
    )
    if created:
        patient_user.set_password('test123')
        patient_user.save()
        print(f"   ✓ Created patient user: {patient_user.email}")
    else:
        print(f"   ℹ Patient user already exists: {patient_user.email}")
    
    # Create patient profile
    patient, created = Patient.objects.get_or_create(
        user=patient_user,
        defaults={
            'date_of_birth': '1990-01-15',
            'gender': 'M',
            'phone_number': '+250788123456',
            'national_id': '1199001501234567',
        }
    )
    if created:
        print(f"   ✓ Created patient profile for {patient_user.get_full_name()}")
    
    # Create nurse user
    print("\n👩‍⚕️ Creating nurse user...")
    nurse_user, created = User.objects.get_or_create(
        username='nurse_demo',
        defaults={
            'email': 'nurse@test.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
        }
    )
    if created:
        nurse_user.set_password('test123')
        nurse_user.save()
        print(f"   ✓ Created nurse user: {nurse_user.email}")
    else:
        print(f"   ℹ Nurse user already exists: {nurse_user.email}")
    
    # Create nurse profile
    nurse_profile, created = NurseProfile.objects.get_or_create(
        user=nurse_user,
        defaults={
            'phone_number': '+250788654321',
            'license_number': 'RN12345',
            'specialization': 'General Care',
            'current_shift': 'morning',
            'status': 'available',
            'max_concurrent_patients': 10,
            'is_active': True,
        }
    )
    if created:
        print(f"   ✓ Created nurse profile for {nurse_user.get_full_name()}")
    
    # Create conversation
    print("\n💬 Creating conversation...")
    conversation, created = Conversation.objects.get_or_create(
        patient=patient,
        nurse=nurse_profile,
    )
    if created:
        print(f"   ✓ Created conversation: {conversation.id}")
    else:
        print(f"   ℹ Conversation already exists: {conversation.id}")
    
    # Create sample messages
    print("\n📨 Creating sample messages...")
    messages_data = [
        (patient_user, "Hello Nurse Smith! I have a question about my medication schedule."),
        (nurse_user, "Hi John! I'm happy to help. What specific questions do you have?"),
        (patient_user, "Should I take my blood pressure medication before or after meals?"),
        (nurse_user, "Great question! For blood pressure medication, it's generally better to take it at the same time each day. The timing relative to meals depends on the specific medication. Which one are you taking?"),
        (patient_user, "I'm taking Amlodipine 5mg."),
        (nurse_user, "Perfect! Amlodipine can be taken with or without food. The most important thing is consistency - take it at the same time every day. Many people find it easiest to take it with breakfast or dinner. What time works best for you?"),
        (patient_user, "I think breakfast would work well for me. Around 8 AM."),
        (nurse_user, "Excellent choice! Taking it with breakfast at 8 AM will help you remember. Set a daily reminder on your phone if that helps. Let me know if you experience any side effects like swelling or dizziness."),
        (patient_user, "Thank you so much! I'll do that. I really appreciate your help!"),
        (nurse_user, "You're very welcome! Feel free to message me anytime if you have questions. Take care! 😊"),
    ]
    
    messages_created = 0
    for sender, content in messages_data:
        message, created = ChatMessage.objects.get_or_create(
            conversation=conversation,
            sender=sender,
            content=content,
        )
        if created:
            messages_created += 1
    
    print(f"   ✓ Created {messages_created} new messages")
    print(f"   ℹ Total messages in conversation: {conversation.messages.count()}")
    
    # Print summary
    print("\n" + "="*60)
    print("✅ Demo data created successfully!")
    print("="*60)
    print(f"\n👤 Patient Login:")
    print(f"   URL: http://localhost:5173/patient/login")
    print(f"   Email: {patient_user.email}")
    print(f"   Password: test123")
    print(f"\n👩‍⚕️ Nurse Login:")
    print(f"   URL: http://localhost:5173/login")
    print(f"   Email: {nurse_user.email}")
    print(f"   Password: test123")
    print(f"\n💬 Conversation ID: {conversation.id}")
    print(f"   Total Messages: {conversation.messages.count()}")
    print("\n" + "="*60)
    print("Next Steps:")
    print("  1. Login as patient at http://localhost:5173/patient/login")
    print("  2. Go to Messages tab")
    print("  3. Open another browser/incognito window")
    print("  4. Login as nurse at http://localhost:5173/login")
    print("  5. Go to Messages section")
    print("  6. Test real-time chat!")
    print("="*60 + "\n")

if __name__ == '__main__':
    create_demo_data()
