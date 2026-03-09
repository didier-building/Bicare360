"""
Create Demo Data for Chat Feature

Creates sample users and conversations for testing the chat feature.

Usage:
    python create_chat_demo_data.py

Author: Didier IMANIRAHARI
Date: March 2026
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from apps.patients.models import Patient
from apps.caregivers.models import Caregiver
from apps.chat.models import Conversation, ChatMessage

User = get_user_model()

def create_demo_data():
    """Create demo users, conversations, and messages."""
    
    print("🚀 Creating demo data for chat feature...\n")
    
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
        print(f"   ✓ Created patient profile for {patient_user.get_full_name}")
    
    # Create caregiver user
    print("\n👩‍⚕️ Creating caregiver user...")
    caregiver_user, created = User.objects.get_or_create(
        username='caregiver_demo',
        defaults={
            'email': 'caregiver@test.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
        }
    )
    if created:
        caregiver_user.set_password('test123')
        caregiver_user.save()
        print(f"   ✓ Created caregiver user: {caregiver_user.email}")
    else:
        print(f"   ℹ Caregiver user already exists: {caregiver_user.email}")
    
    # Create caregiver profile
    caregiver, created = Caregiver.objects.get_or_create(
        user=caregiver_user,
        defaults={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'caregiver@test.com',
            'phone_number': '+250788654321',
            'profession': 'registered_nurse',
            'experience_years': 5,
            'bio': 'Experienced registered nurse specializing in chronic disease management.',
            'province': 'Kigali',
            'district': 'Gasabo',
            'hourly_rate': 45.00,
            'is_verified': True,
            'availability_status': 'available',
        }
    )
    if created:
        print(f"   ✓ Created caregiver profile for {caregiver_user.get_full_name}")
    
    # Create conversation
    print("\n💬 Creating conversation...")
    conversation, created = Conversation.objects.get_or_create(
        patient=patient,
        caregiver=caregiver,
    )
    if created:
        print(f"   ✓ Created conversation: {conversation.id}")
    else:
        print(f"   ℹ Conversation already exists: {conversation.id}")
    
    # Create sample messages
    print("\n📨 Creating sample messages...")
    messages_data = [
        (patient_user, "Hello Dr. Smith! I have a question about my medication schedule."),
        (caregiver_user, "Hi John! I'm happy to help. What specific questions do you have?"),
        (patient_user, "Should I take my blood pressure medication before or after meals?"),
        (caregiver_user, "Great question! For blood pressure medication, it's generally better to take it at the same time each day. The timing relative to meals depends on the specific medication. Which one are you taking?"),
        (patient_user, "I'm taking Amlodipine 5mg."),
        (caregiver_user, "Perfect! Amlodipine can be taken with or without food. The most important thing is consistency - take it at the same time every day. Many people find it easiest to take it with breakfast or dinner. What time works best for you?"),
        (patient_user, "I think breakfast would work well for me. Around 8 AM."),
        (caregiver_user, "Excellent choice! Taking it with breakfast at 8 AM will help you remember. Set a daily reminder on your phone if that helps. Let me know if you experience any side effects like swelling or dizziness."),
        (patient_user, "Thank you so much! I'll do that. I really appreciate your help!"),
        (caregiver_user, "You're very welcome! Feel free to message me anytime if you have questions. Take care! 😊"),
    ]
    
    created_count = 0
    for sender, content in messages_data:
        message, created = ChatMessage.objects.get_or_create(
            conversation=conversation,
            sender=sender,
            content=content,
            defaults={'is_read': True}
        )
        if created:
            created_count += 1
    
    print(f"   ✓ Created {created_count} sample messages")
    
    # Summary
    print("\n" + "="*60)
    print("✅ Demo data creation complete!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"   • Patient: {patient_user.email} / password: test123")
    print(f"   • Caregiver: {caregiver_user.email} / password: test123")
    print(f"   • Conversation ID: {conversation.id}")
    print(f"   • Total Messages: {ChatMessage.objects.filter(conversation=conversation).count()}")
    print("\n🌐 Access Points:")
    print(f"   • Patient Login: http://localhost:5173/patient/login")
    print(f"   • Patient Chat: http://localhost:5173/patient/messages")
    print(f"   • Caregiver Login: http://localhost:5173/login")
    print(f"   • Caregiver Chat: http://localhost:5173/messages")
    print("\n💡 Next Steps:")
    print("   1. Login as patient (patient@test.com / test123)")
    print("   2. Navigate to Messages")
    print("   3. Open a second browser window as caregiver")
    print("   4. Send messages and see real-time delivery!")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    create_demo_data()
