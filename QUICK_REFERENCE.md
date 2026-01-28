# 🔍 BiCare360 - Quick Reference Guide & Common Queries

**A practical guide to understanding and querying the BiCare360 system**

---

## 🎯 What Problem Does BiCare360 Solve?

### The Core Issue
Post-hospital discharge patients in Rwanda (and Africa broadly) have **zero structured follow-up**, resulting in:
- 🔴 **Non-adherence**: Patients stop taking medications after 2-3 weeks
- 🔴 **Missed Appointments**: No reminder system for follow-ups
- 🔴 **Preventable Readmissions**: Early complications go undetected
- 🔴 **Poor Outcomes**: High mortality despite successful hospital treatment
- 🔴 **Wasted Resources**: Hospitals readmit same patients (unnecessary costs)

### The BiCare360 Solution

```
Before BiCare360:
Hospital Discharge → Blank Check → Lost Patient → Readmission (unnecessary)

After BiCare360:
Hospital Discharge 
    ↓ [Comprehensive Discharge Summary + Risk Assessment]
Home Management 
    ↓ [Automated SMS Reminders for Meds + Appointments]
Nurse Monitoring 
    ↓ [Alerts for Missed Meds/Appointments + Triage]
Positive Outcome 
    ↓ [Prevents Readmission + Improves Health]
```

---

## 📊 Core Business Model

### The "Hybrid Care Bridge" Components

| # | Component | When | Who Manages | Problem Solved |
|---|-----------|------|------------|---|
| 1 | **Bedside Handoff** | At discharge | Hospital + Nurse | Incomplete discharge info |
| 2 | **Patient Management** | Ongoing | System | Patient data inconsistency |
| 3 | **Medication Tracking** | Daily | Nurse + System | Non-adherence |
| 4 | **Appointment Management** | Weekly | Patient + Nurse | Missed follow-ups |
| 5 | **Alert Triage** | 24/7 | Nurse | No response to complications |
| 6 | **Digital Companion** | 24/7 | AI Chatbot | No patient education |
| 7 | **Abafasha Guides** | As needed | Care Coordinator | No in-person support |
| 8 | **Analytics** | Monthly | Hospital Admin | No outcome tracking |

### Revenue Streams
- **Per-Patient Fee**: $2-5/patient/month (from hospitals)
- **Hospital License**: $5K-10K/hospital/year
- **Insurance Savings**: Revenue share on prevented readmissions
- **Volume**: 50K+ hospital discharges/year in Rwanda alone

---

## 💾 Database Relationships (Simple View)

### "A Patient's Journey" - How Data Flows

```
1. PATIENT IS ADMITTED
   └─ Patient model created (if not exists)
      ├─ first_name, last_name, national_id, phone
      ├─ date_of_birth, gender, blood_type
      └─ language_preference (Kinyarwanda or English)

2. PATIENT IS DISCHARGED
   └─ DischargeSummary created
      ├─ diagnosis (ICD-10 code)
      ├─ risk_assessment (low/medium/high/critical)
      ├─ discharge_instructions (bilingual)
      ├─ follow_up_timeframe ("1 week")
      └─ attending_physician info

3. PRESCRIPTIONS ARE ADDED
   ├─ Prescription #1: Aspirin 500mg × 3 daily × 14 days
   ├─ Prescription #2: Metformin 1000mg × 2 daily × 30 days
   └─ Prescription #3: Lisinopril 10mg × 1 daily × 60 days

4. APPOINTMENTS ARE SCHEDULED
   ├─ Follow-up appointment (1 week) with Dr. X
   └─ Medication review (2 weeks)

5. ALERTS ARE CREATED (AUTOMATICALLY)
   ├─ "Follow-up needed" (status=new, severity=high)
   ├─ "Monitor blood pressure" (from discharge summary)
   └─ "Check medication adherence" (weekly)

6. NURSE IS ASSIGNED
   ├─ NurseProfile finds available nurse
   ├─ Assigns alerts to nurse
   └─ NursePatientAssignment tracks ongoing relationship

7. DAILY MONITORING (AUTOMATED)
   ├─ EACH MORNING: Generate AdherenceLog for scheduled doses
   ├─ EACH AFTERNOON: Check for overdue doses
   │  └─ If dose missed → Send SMS reminder
   │  └─ If still missed by evening → Create 'missed_medication' alert
   ├─ DAY BEFORE APPOINTMENT: Send appointment reminder
   └─ WEEKLY: Calculate adherence rate + readmission risk score

8. PATIENT ACTIONS
   ├─ Takes medication → Logs in app → Updates AdherenceLog.status='taken'
   ├─ Misses medication → Nurse sends SMS → Patient replies "TAKEN"
   ├─ Attends appointment → Appointment.status='completed'
   └─ Reports symptoms → Creates PatientAlert type='symptom_report'

9. NURSE ACTIONS
   ├─ Views alerts dashboard
   ├─ Calls patient (if critical alert)
   ├─ Schedules home visit if needed
   ├─ Updates patient info/prescriptions
   ├─ Marks alert resolved
   └─ Documents everything in AlertLog (audit trail)

10. OUTCOMES
    ├─ Patient adheres to medications
    ├─ Attends follow-up appointments
    ├─ Complications detected early (via alerts)
    ├─ Prevented readmission
    └─ Hospital reports: "Saved 1 readmission = $5K savings"
```

---

## 🔧 Common Development Tasks

### Task 1: "I Want to Add a New Medication"

**Location**: `backend/apps/medications/models.py`

**Process**:
```python
# 1. Add Medication via Django Admin
# OR via API: POST /api/v1/medications/
# {
#   "generic_name": "Aspirin",
#   "brand_names": ["Bayer", "Disprin"],
#   "dosage_form": "tablet",
#   "strength": "500mg",
#   "manufacturer": "Roche Rwanda"
# }

# 2. The system stores it in Medication model
# 3. Nurses can now prescribe it to patients
# 4. Patients get reminders via SMS
```

---

### Task 2: "I Want to Understand Patient X's Status"

**Check These in Order**:

```python
# 1. PATIENT BASICS
GET /api/v1/patients/{patient_id}/
# Returns: name, ID, phone, emergency contacts, addresses

# 2. DISCHARGE HISTORY
GET /api/v1/enrollment/discharge-summaries/?patient={patient_id}
# Returns: diagnosis, risk level, follow-up needs, discharge date

# 3. MEDICATIONS (What they should be taking)
GET /api/v1/prescriptions/?patient={patient_id}&status=current
# Returns: medications, dosages, frequency, instructions

# 4. ADHERENCE (Are they taking meds?)
GET /api/v1/adherence/?patient={patient_id}&days=7
# Returns: doses taken/missed, times, reasons

# 5. APPOINTMENTS (Follow-ups scheduled)
GET /api/v1/appointments/?patient={patient_id}&status=scheduled
# Returns: appointment dates, providers, locations

# 6. ALERTS (Issues needing attention)
GET /api/v1/nursing/alerts/?patient={patient_id}&status=new
# Returns: unresolved issues, severity, SLA deadlines

# 7. VITAL SIGNS (If patient tracking them)
GET /api/v1/vitals/?patient={patient_id}
# Returns: BP, heart rate, weight trends

# SUMMARY: If alerts=many + adherence<60% + missed_appointments=yes
#  → Patient is high-risk → Nurse should intervene
```

---

### Task 3: "I Want to Create a New Alert for a Patient"

**Manually via API** (usually system-generated, but nurses can create):

```bash
POST /api/v1/nursing/alerts/
{
  "patient": 123,
  "alert_type": "symptom_report",
  "severity": "high",
  "title": "Patient reports chest pain",
  "description": "Called nurse reporting chest pain after exercise"
}

# Response:
{
  "id": 456,
  "status": "new",
  "created_at": "2026-01-28T10:30:00Z",
  "due_at": "2026-01-28T10:40:00Z",  # 10-minute SLA
  "assigned_nurse": null  # Waiting for assignment
}
```

---

### Task 4: "I Want to Assign an Alert to a Nurse"

```bash
# Check which nurses are available
GET /api/v1/nursing/profiles/available/
# Returns: nurses with is_available_for_assignment=true

# Assign alert to a specific nurse
PATCH /api/v1/nursing/alerts/456/assign/
# Header: Authorization: Bearer {nurse_jwt_token}

# Response:
{
  "id": 456,
  "status": "assigned",
  "assigned_nurse": 789,
  "assigned_at": "2026-01-28T10:32:00Z"
}

# Now nurse (789) can see in their dashboard
```

---

### Task 5: "I Want to Track Medication Adherence"

**Manual Dose Tracking**:
```bash
# Patient took medication
POST /api/v1/adherence/
{
  "prescription": 123,
  "dose_date": "2026-01-28",
  "dose_time": "08:00",
  "status": "taken"
}

# Patient missed dose
POST /api/v1/adherence/
{
  "prescription": 123,
  "dose_date": "2026-01-28",
  "dose_time": "14:00",
  "status": "missed",
  "reason_missed": "Forgot to take with lunch"
}

# System automatically checks daily:
# - AdherenceLog where scheduled_time < now() and status='scheduled'
# - If overdue since morning → Send SMS reminder
# - If overdue since evening → Create 'missed_medication' alert
```

---

### Task 6: "I Want to See Patient Adherence Trends"

```bash
# Get last 30 days of adherence
GET /api/v1/adherence/?patient={patient_id}&days=30

# Calculate from response:
total_doses = 42 (7 days × 3 meds × 2 doses/day)
doses_taken = 38
doses_missed = 3
doses_skipped = 1

adherence_rate = (38 + 1) / 42 × 100% = 92.8% ✅
```

---

## 🎯 Key Decision Points (For Developers)

### "Should I Create an Alert?"

```
IF patient discharged with high/critical risk
   AND no follow-up appointment scheduled
   AND follow_up_required = True
   THEN create 'follow_up_needed' alert

IF prescription due to end in 3 days
   AND no refill request submitted
   THEN create 'refill_request' alert

IF adherence rate last 7 days < 70%
   AND not already an active alert
   THEN create 'low_adherence' alert

IF appointment is tomorrow
   AND appointment_status = 'scheduled'
   AND reminder not yet sent
   THEN create 'upcoming_appointment' alert

IF vital sign reading is abnormal
   AND marked is_abnormal = True
   THEN create 'symptom_report' alert
```

### "When Should I Send a Message?"

```
SEND SMS when:
- Appointment in 24 hours (reminder)
- Medication dose overdue (reminder to take)
- Alert created (notify nurse/patient)
- Prescription refill available (notify patient)
- Appointment confirmed/changed (confirmation)

SEND EMAIL when:
- Account creation (activation link)
- Report generated (monthly summary)
- Important alert (backup channel)

SEND WHATSAPP when:
- Preferred channel in privacy preferences
- More interactive (links, buttons)
- Follow-up to SMS (richer interface)
```

---

## 📊 Understanding the 8 Alert Types

```
1. MISSED_MEDICATION
   Trigger: AdherenceLog.status = 'missed' (evening check)
   Severity: HIGH (non-adherence = readmission risk)
   SLA: 2 hours (nurse should call by evening)
   Action: Nurse provides education, updates prescription if needed

2. MISSED_APPOINTMENT
   Trigger: Appointment past scheduled time + status still scheduled
   Severity: MEDIUM
   SLA: 4 hours
   Action: Reschedule appointment, understand patient barriers

3. HIGH_RISK_DISCHARGE
   Trigger: DischargeSummary.risk_assessment = 'critical'
   Severity: CRITICAL
   SLA: 10 minutes
   Action: Nurse calls patient day 1 post-discharge

4. SYMPTOM_REPORT
   Trigger: VitalReading.is_abnormal = True OR patient self-reports
   Severity: HIGH (if abnormal)
   SLA: 30 minutes
   Action: Nurse assesses, escalates to doctor if needed

5. READMISSION_RISK
   Trigger: Predictive scoring (missed meds + missed appts + abnormal vitals)
   Severity: MEDIUM → HIGH
   SLA: 24 hours
   Action: Nurse increases contact frequency, preventive intervention

6. MEDICATION_SIDE_EFFECT
   Trigger: Patient reports side effect via SMS/app
   Severity: HIGH
   SLA: 1 hour
   Action: Escalate to doctor, consider medication change

7. EMERGENCY
   Trigger: Patient marks symptom as emergency (chest pain, etc.)
   Severity: CRITICAL
   SLA: 5 minutes
   Action: Immediate escalation, ambulance call coordination

8. FOLLOW_UP_NEEDED
   Trigger: DischargeSummary.follow_up_required = True + timeframe reached
   Severity: MEDIUM
   SLA: 24 hours
   Action: Schedule appointment if not already booked
```

---

## 🔐 Understanding Permissions

```
WHO CAN DO WHAT:

Patient (authenticated via JWT):
✅ View own profile
✅ View own appointments + medications + alerts
✅ Schedule appointment
✅ Reschedule own appointment
✅ Cancel own appointment
✅ Log medication adherence (take/miss)
✅ Upload vital signs
✅ View health goals
❌ View other patients
❌ Assign alerts
❌ Create medications
❌ Access admin panel

Nurse (has NurseProfile):
✅ View all alerts
✅ View all patients (assigned to them)
✅ Create alerts
✅ Assign alerts to self
✅ Resolve alerts
✅ View medication adherence trends
✅ Schedule appointments on behalf of patient
❌ Delete alerts
❌ Create medications
❌ Access hospital admin

Hospital Admin:
✅ View all patients in hospital
✅ View discharge summaries
✅ Manage staff (nurses)
✅ View analytics + dashboards
✅ Create appointments
✅ Generate reports
❌ Modify patient data
❌ Access other hospitals

System Admin:
✅ Everything (Django superuser)
```

---

## 🧮 Common Calculations

### 1. Patient Risk Score (0-100)

```python
def calculate_risk_score(patient):
    score = 0
    
    # Discharge risk (base)
    if discharge.risk_assessment == 'critical':
        score += 40
    elif discharge.risk_assessment == 'high':
        score += 25
    
    # Medication adherence
    adherence_rate = patient.get_adherence_rate(days=7)
    if adherence_rate < 50:
        score += 30
    elif adherence_rate < 70:
        score += 15
    
    # Appointment adherence
    missed_appts = patient.appointments.filter(
        status='no_show',
        appointment_datetime__gte=7_days_ago
    ).count()
    if missed_appts >= 2:
        score += 20
    
    # Abnormal vitals
    abnormal_vitals = patient.vitals.filter(
        is_abnormal=True,
        reading_date__gte=7_days_ago
    ).count()
    if abnormal_vitals > 0:
        score += 15
    
    return min(score, 100)  # Cap at 100

# Risk Level:
# 0-25: Low (routine monitoring)
# 26-50: Medium (weekly check-in)
# 51-75: High (2-3x weekly contact)
# 76-100: Critical (daily contact + home visit)
```

### 2. Medication Adherence Rate

```python
def calculate_adherence(prescription, days=30):
    adherence_logs = prescription.adherence_logs.filter(
        dose_date__gte=today - days
    )
    
    total_scheduled = adherence_logs.count()
    taken_or_skipped = adherence_logs.filter(
        status__in=['taken', 'skipped']
    ).count()
    
    return (taken_or_skipped / total_scheduled * 100) if total_scheduled > 0 else 0
```

### 3. SLA Compliance

```python
def calculate_sla_compliance(nurse, period_days=30):
    alerts = Alert.objects.filter(
        assigned_nurse=nurse,
        assigned_at__gte=today - period_days
    )
    
    on_time = alerts.filter(
        resolved_at__lte=F('due_at')  # Resolved before deadline
    ).count()
    
    return (on_time / alerts.count() * 100) if alerts.count() > 0 else 100
```

---

## 🐛 Debugging Common Issues

### "Patient Can't See Their Appointments"

**Check**:
1. Patient authenticated? → `GET /api/v1/appointments/my/` requires JWT
2. Appointments exist? → `GET /api/v1/appointments/?patient={id}`
3. Permission granted? → Check `IsOwnPatient` permission
4. Status correct? → Canceled appointments shouldn't show

### "Medication Adherence Not Tracking"

**Check**:
1. Prescription created? → `GET /api/v1/prescriptions/?patient={id}`
2. Dates correct? → `prescription.is_current` should be True
3. AdherenceLog records exist? → `GET /api/v1/adherence/?prescription={id}`
4. Celery task running? → Check background job logs

### "Alert Not Assigned to Nurse"

**Check**:
1. Nurse available? → `nurse.is_available_for_assignment` must be True
2. Nurse at capacity? → `nurse.current_patient_count < max_concurrent`
3. Alert exists? → `Alert.status` must be 'new'
4. Permission error? → Check `CanAssignAlert` permission

---

## 🚀 Quick API Usage Examples

### Example 1: Create Patient & Discharge Summary

```bash
# 1. Create patient
curl -X POST http://localhost:8000/api/v1/patients/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "first_name": "Jean",
    "last_name": "Ndamyumvira",
    "national_id": "1234567890123456",
    "phone_number": "+250788123456",
    "date_of_birth": "1985-05-15",
    "gender": "M"
  }'

# Response:
{
  "id": 1,
  "full_name": "Jean Ndamyumvira",
  "national_id": "1234567890123456"
}

# 2. Create discharge summary
curl -X POST http://localhost:8000/api/v1/enrollment/discharge-summaries/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "patient": 1,
    "hospital": 1,
    "admission_date": "2026-01-20",
    "discharge_date": "2026-01-28",
    "primary_diagnosis": "Type 2 Diabetes Mellitus",
    "icd10_primary": "E11",
    "risk_assessment": "high",
    "discharge_instructions": "Take medications daily, check blood sugar",
    "discharge_instructions_kinyarwanda": "Funzira inzira zose ...",
    "follow_up_required": true,
    "follow_up_timeframe": "1 week"
  }'

# System automatically:
# - Calculates length_of_stay
# - Marks as high-risk
# - Creates alert: 'follow_up_needed'
```

### Example 2: Track Medication Adherence

```bash
# Patient logs dose
curl -X POST http://localhost:8000/api/v1/adherence/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "prescription": 1,
    "dose_date": "2026-01-28",
    "dose_time": "08:00",
    "status": "taken"
  }'

# Or patient misses dose
curl -X POST http://localhost:8000/api/v1/adherence/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "prescription": 1,
    "dose_date": "2026-01-28",
    "dose_time": "14:00",
    "status": "missed",
    "reason_missed": "Forgot"
  }'

# Nurse checks adherence
curl -X GET "http://localhost:8000/api/v1/adherence/?prescription=1&days=7" \
  -H "Authorization: Bearer TOKEN"

# Response: [
#   { "dose_date": "2026-01-22", "status": "taken", "dose_time": "08:00" },
#   { "dose_date": "2026-01-23", "status": "missed", "reason_missed": "Forgot" },
#   ...
# ]
```

### Example 3: Manage Alerts

```bash
# Create alert (system or nurse)
curl -X POST http://localhost:8000/api/v1/nursing/alerts/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "patient": 1,
    "alert_type": "missed_medication",
    "severity": "high",
    "title": "Missed dose today",
    "description": "Patient didnt take 2PM dose of Aspirin"
  }'

# Assign to self (nurse)
curl -X PATCH http://localhost:8000/api/v1/nursing/alerts/1/assign/ \
  -H "Authorization: Bearer NURSE_TOKEN"

# Resolve alert
curl -X PATCH http://localhost:8000/api/v1/nursing/alerts/1/resolve/ \
  -H "Authorization: Bearer NURSE_TOKEN" \
  -d '{
    "resolution_notes": "Called patient, explained importance of adherence"
  }'
```

---

## 📈 Reporting Common Metrics

### Hospital Administrator View

```bash
# 1. Total discharges this month
GET /api/v1/enrollment/discharge-summaries/?start_date=2026-01-01

# 2. High-risk patients
GET /api/v1/enrollment/discharge-summaries/high_risk/

# 3. Average appointment attendance rate
GET /api/v1/appointments/?status=completed&start_date=2026-01-01
# Divide by total appointments

# 4. Average medication adherence
GET /api/v1/adherence/?start_date=2026-01-01
# Calculate (taken + skipped) / total

# 5. Alert response time (SLA compliance)
GET /api/v1/nursing/alerts/?resolved=true
# Filter: resolved_at <= due_at

# 6. Readmission rate
GET /api/v1/enrollment/discharge-summaries/
# Count where days_since_discharge < 30 AND patient_readmitted = true
```

---

## 🎓 Learning Resources Within the Code

1. **Model Examples**: [backend/apps/nursing/models.py](backend/apps/nursing/models.py)
   - See how `PatientAlert` tracks severity + SLA

2. **Serializer Examples**: [backend/apps/appointments/serializers.py](backend/apps/appointments/serializers.py)
   - See how validation works

3. **ViewSet Examples**: [backend/apps/enrollment/views.py](backend/apps/enrollment/views.py)
   - See how `custom_actions` for filters work

4. **Test Examples**: [backend/apps/nursing/tests/](backend/apps/nursing/tests/)
   - See how to test alerts + assignment

5. **Frontend Examples**: [frontend/src/pages/PatientAppointmentsPage.tsx](frontend/src/pages/PatientAppointmentsPage.tsx)
   - See how to integrate with API + UI

---

## 🏁 Success Criteria

### "Is Patient X Being Well Monitored?"

Check if all boxes are ✅:

- ✅ Discharge summary created with risk assessment
- ✅ Medications prescribed with clear instructions
- ✅ Follow-up appointment scheduled
- ✅ Alert created for follow-up
- ✅ Nurse assigned to patient
- ✅ Daily adherence tracking active
- ✅ Appointment reminder sent 24h before
- ✅ Abnormal vitals trigger alerts
- ✅ Missed doses create alerts within 4 hours
- ✅ SLA response met (nurse contacts within timeframe)

If any ❌, the system needs fixing!

---

**This quick reference covers ~80% of common questions. For detailed info, see [CODEBASE_INDEX.md](CODEBASE_INDEX.md).**

