"""
Create sample data for Nurse Dashboard testing
"""
from django.contrib.auth.models import User
from apps.nursing.models import NurseProfile, PatientAlert, NursePatientAssignment
from apps.patients.models import Patient
from apps.enrollment.models import DischargeSummary

# Create 5 nurses
print("Creating nurses...")
for i in range(1, 6):
    user, created = User.objects.get_or_create(
        username=f'nurse{i}',
        defaults={
            'first_name': ['John', 'Sarah', 'Michael', 'Emily', 'David'][i-1],
            'last_name': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'][i-1],
            'email': f'nurse{i}@bicare360.rw'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    
    nurse, created = NurseProfile.objects.get_or_create(
        user=user,
        defaults={
            'license_number': f'RN{10000 + i}',
            'phone_number': f'+25078812345{i}',
            'specialization': ['ER', 'ICU', 'Cardiology', 'General', 'Pediatrics'][i-1],
            'current_shift': ['morning', 'morning', 'afternoon', 'afternoon', 'night'][i-1],
            'status': 'available',
            'max_concurrent_patients': 8,
            'is_active': True
        }
    )
    if created:
        print(f"  Created: {nurse}")

# Get existing patients (from previous tests)
patients = Patient.objects.all()[:10]
print(f"\nFound {patients.count()} patients")

if patients.count() >= 3:
    # Create some alerts
    print("\nCreating patient alerts...")
    nurses = list(NurseProfile.objects.all())
    
    alert_data = [
        {
            'patient': patients[0],
            'alert_type': 'missed_medication',
            'severity': 'high',
            'title': 'Missed Morning Blood Pressure Medication',
            'description': 'Patient did not take prescribed morning BP medication',
            'assigned_nurse': nurses[0] if nurses else None,
            'status': 'new'
        },
        {
            'patient': patients[1],
            'alert_type': 'high_risk_discharge',
            'severity': 'critical',
            'title': 'High Readmission Risk - Diabetes',
            'description': 'Patient discharged with uncontrolled blood sugar levels',
            'assigned_nurse': nurses[1] if len(nurses) > 1 else None,
            'status': 'assigned'
        },
        {
            'patient': patients[2],
            'alert_type': 'missed_appointment',
            'severity': 'medium',
            'title': 'Missed Follow-up Appointment',
            'description': 'Patient missed scheduled post-discharge check-up',
            'assigned_nurse': nurses[2] if len(nurses) > 2 else None,
            'status': 'in_progress'
        },
        {
            'patient': patients[0],
            'alert_type': 'symptom_report',
            'severity': 'high',
            'title': 'Patient Reported Chest Pain',
            'description': 'Patient called reporting chest discomfort and shortness of breath',
            'assigned_nurse': nurses[0] if nurses else None,
            'status': 'new'
        },
        {
            'patient': patients[1],
            'alert_type': 'medication_side_effect',
            'severity': 'medium',
            'title': 'Reported Medication Side Effects',
            'description': 'Patient experiencing nausea from new medication',
            'assigned_nurse': nurses[1] if len(nurses) > 1 else None,
            'status': 'assigned'
        },
    ]
    
    for data in alert_data:
        alert, created = PatientAlert.objects.get_or_create(
            patient=data['patient'],
            title=data['title'],
            defaults=data
        )
        if created:
            print(f"  Created: {alert}")
    
    # Create some assignments (if we have discharge summaries)
    discharge_summaries = DischargeSummary.objects.all()[:3]
    if discharge_summaries.exists() and nurses:
        print("\nCreating nurse-patient assignments...")
        for i, ds in enumerate(discharge_summaries):
            assignment, created = NursePatientAssignment.objects.get_or_create(
                nurse=nurses[i % len(nurses)],
                patient=ds.patient,
                discharge_summary=ds,
                defaults={
                    'status': 'active',
                    'priority': [3, 2, 1][i],
                    'notes': f'Post-discharge monitoring for {ds.patient.get_full_name()}'
                }
            )
            if created:
                print(f"  Created: {assignment}")
    
    print(f"\n✅ Sample data created successfully!")
    print(f"   - Nurses: {NurseProfile.objects.count()}")
    print(f"   - Alerts: {PatientAlert.objects.count()}")
    print(f"   - Assignments: {NursePatientAssignment.objects.count()}")
else:
    print("\n⚠️  Not enough patients in database. Run patient fixtures first.")
