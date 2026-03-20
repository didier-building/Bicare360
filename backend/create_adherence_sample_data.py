"""
Create sample medication adherence records for testing.
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings')
django.setup()

from django.utils import timezone
from apps.patients.models import Patient
from apps.medications.models import Prescription, MedicationAdherence, Medication

def create_adherence_records():
    """Create adherence records for all active prescriptions."""
    
    # Get all active prescriptions
    prescriptions = Prescription.objects.filter(is_active=True).select_related('patient', 'medication')
    
    if not prescriptions.exists():
        print("No active prescriptions found. Creating sample medications and prescriptions for ALL patients...")
        
        # Get or create medications
        medications = []
        med_data = [
            ('Paracetamol', 'Acetaminophen', 'tablet', '500mg'),
            ('Ibuprofen', 'Ibuprofen', 'tablet', '400mg'),
            ('Amoxicillin', 'Amoxicillin', 'capsule', '250mg'),
            ('Omeprazole', 'Omeprazole', 'capsule', '20mg'),
        ]
        
        for name, generic, form, strength in med_data:
            medication, _ = Medication.objects.get_or_create(
                name=name,
                defaults={
                    'generic_name': generic,
                    'dosage_form': form,
                    'strength': strength,
                    'manufacturer': 'Generic Pharma',
                    'requires_prescription': False,
                    'is_active': True,
                }
            )
            medications.append(medication)
        
        # Get ALL patients
        patients = Patient.objects.all()
        if not patients.exists():
            print("❌ No patients found in database!")
            return
        
        print(f"📋 Creating prescriptions for {patients.count()} patients...")
        
        # Create prescriptions for each patient
        import random
        prescriptions = []
        for patient in patients:
            # Give each patient 1-2 prescriptions
            num_prescriptions = random.randint(1, 2)
            for _ in range(num_prescriptions):
                medication = random.choice(medications)
                freq_times = random.choice([1, 2, 3])
                
                prescription = Prescription.objects.create(
                    patient=patient,
                    medication=medication,
                    dosage=medication.strength,
                    frequency=f'{freq_times} times daily' if freq_times > 1 else 'Once daily',
                    frequency_times_per_day=freq_times,
                    route='oral',
                    duration_days=14,
                    quantity=freq_times * 14,
                    start_date=timezone.now().date() - timedelta(days=3),
                    end_date=timezone.now().date() + timedelta(days=11),
                    is_active=True,
                )
                prescriptions.append(prescription)
        
        print(f"✅ Created {len(prescriptions)} prescriptions")
    
    created_count = 0
    
    for prescription in prescriptions:
        print(f"\n📋 Processing: {prescription.medication.name} for {prescription.patient.first_name} {prescription.patient.last_name}")
        
        # Generate adherence records for the last 7 days
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()
        
        for day_offset in range(8):  # 7 days + today
            scheduled_date = start_date + timedelta(days=day_offset)
            
            # Create records based on frequency_times_per_day
            for time_slot in range(prescription.frequency_times_per_day):
                # Generate time slots throughout the day
                hour = 8 + (time_slot * (12 // prescription.frequency_times_per_day))
                scheduled_time = f"{hour:02d}:00:00"
                
                # Check if record already exists
                existing = MedicationAdherence.objects.filter(
                    prescription=prescription,
                    patient=prescription.patient,
                    scheduled_date=scheduled_date,
                    scheduled_time=scheduled_time
                ).first()
                
                if existing:
                    continue
                
                # Determine status (mix of taken/missed/pending)
                if scheduled_date < timezone.now().date():
                    # Past dates: 80% taken, 20% missed
                    import random
                    status = 'taken' if random.random() < 0.8 else 'missed'
                    taken_at = timezone.now() if status == 'taken' else None
                elif scheduled_date == timezone.now().date() and hour < timezone.now().hour:
                    # Today but past time: 70% taken
                    status = 'taken' if random.random() < 0.7 else 'missed'
                    taken_at = timezone.now() if status == 'taken' else None
                else:
                    # Future: pending
                    status = 'pending'
                    taken_at = None
                
                # Create adherence record
                MedicationAdherence.objects.create(
                    prescription=prescription,
                    patient=prescription.patient,
                    scheduled_date=scheduled_date,
                    scheduled_time=scheduled_time,
                    status=status,
                    taken_at=taken_at,
                    notes='Auto-generated' if status == 'taken' else '',
                    reason_missed='Forgot' if status == 'missed' else '',
                )
                created_count += 1
    
    print(f"\n✅ Created {created_count} adherence records")
    
    # Show summary
    total = MedicationAdherence.objects.count()
    taken = MedicationAdherence.objects.filter(status='taken').count()
    missed = MedicationAdherence.objects.filter(status='missed').count()
    pending = MedicationAdherence.objects.filter(status='pending').count()
    
    print(f"\n📊 Adherence Summary:")
    print(f"   Total: {total}")
    print(f"   Taken: {taken}")
    print(f"   Missed: {missed}")
    print(f"   Pending: {pending}")
    if taken + missed > 0:
        adherence_rate = (taken / (taken + missed)) * 100
        print(f"   Adherence Rate: {adherence_rate:.1f}%")

if __name__ == '__main__':
    print("Creating sample medication adherence records...")
    create_adherence_records()
