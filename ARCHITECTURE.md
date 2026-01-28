# 🏗️ BiCare360 - System Architecture & Data Flow

**Visual guide to understanding how BiCare360 works**

---

## 1️⃣ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BiCare360 SYSTEM ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────────────┘

                          ┌─────────────────────┐
                          │   React Frontend    │
                          │  (Patient + Nurse   │
                          │   Dashboards)       │
                          └──────────┬──────────┘
                                     │
                        ┌────────────┴────────────┐
                        │   API (Django + DRF)   │
                        │   Port 8000            │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
    ┌─────▼──────┐          ┌────────▼──────┐        ┌─────────▼──────┐
    │ PostgreSQL │          │   Celery      │        │ Redis Cache    │
    │ Database   │          │   Task Queue  │        │                │
    └────────────┘          └────────┬──────┘        └────────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │  Africa's Talking API   │
                        │  (SMS + WhatsApp)       │
                        └─────────────────────────┘
```

---

## 2️⃣ Data Model Relationships

### Core Entities

```
╔════════════════════════════════════════════════════════════════╗
║                    PATIENT ENROLLMENT FLOW                     ║
╚════════════════════════════════════════════════════════════════╝

┌─────────────┐
│   PATIENT   │  (Demographics, Contact Info)
│   ├─────────┼─────────► Phone: +250788123456 (Rwanda format)
│   ├─────────┼─────────► National ID: 16 digits (validated)
│   └─────────┼─────────► Language: Kinyarwanda or English
└──────┬──────┘
       │
       ├─────► ADDRESS (1:Many) ─────► Province/District/Sector/Cell/Village
       │
       ├─────► EMERGENCY_CONTACT (1:Many) ─────► Relative/Friend phone
       │
       └─────► HOSPITAL (through Discharge Summary)


┌──────────────────────┐
│ DISCHARGE_SUMMARY    │  (Capture everything at discharge)
│ ├────────────────────┼──────────► ICD-10 Diagnosis codes
│ ├────────────────────┼──────────► Risk Assessment: Low/Medium/High/Critical
│ ├────────────────────┼──────────► Instructions (Bilingual)
│ ├────────────────────┼──────────► Follow-up Requirements
│ └────────────────────┼──────────► Provider Info
└──────┬───────────────┘
       │
       ├──► PRESCRIPTION (1:Many) ────────► Medication + Dosage + Duration
       │                                    (Each triggers AdherenceLog entries)
       │
       ├──► APPOINTMENT (1:Many) ──────────► Follow-up visits scheduled
       │                                    (Each triggers Reminder)
       │
       └──► PATIENT_ALERT (1:Many) ────────► High-risk → Auto-create alert
                                            │ + Follow-up needed → Alert
                                            └─ Severity based on risk assessment
```

---

## 3️⃣ Medication Adherence Tracking (Most Complex)

```
┌────────────────────────────────────────────────────────────────┐
│                 MEDICATION ADHERENCE SYSTEM                    │
└────────────────────────────────────────────────────────────────┘

PRESCRIPTION CREATED:
├─ Medication: Aspirin
├─ Dosage: 500mg
├─ Frequency: 3 times daily (8 AM, 2 PM, 8 PM)
├─ Start: 2026-01-28
├─ End: 2026-02-11 (14 days)
└─ Duration: 42 total doses

                              ↓ (System generates)

ADHERENCE_LOG ENTRIES (one per scheduled dose):
┌─────────────────────────────────────────────┐
│ Day 1 (Jan 28)                              │
├─────────────────────────────────────────────┤
│ Dose 1: 8:00 AM   status=scheduled          │
│ Dose 2: 2:00 PM   status=scheduled          │
│ Dose 3: 8:00 PM   status=scheduled          │
├─────────────────────────────────────────────┤
│ Day 2 (Jan 29)                              │
├─────────────────────────────────────────────┤
│ Dose 4: 8:00 AM   status=scheduled          │
│ Dose 5: 2:00 PM   status=scheduled          │
│ Dose 6: 8:00 PM   status=scheduled          │
│                                             │
│ ... (36 more doses for remaining 12 days)  │
└─────────────────────────────────────────────┘

                              ↓ (Patient/System updates)

PATIENT ACTIONS:
┌─────────────────────────────────────────────┐
│ Jan 28, 8:00 AM                             │
│ Patient wakes up, takes pill                │
│ → Update: status=taken, taken_time=08:15   │
├─────────────────────────────────────────────┤
│ Jan 28, 2:00 PM                             │
│ Patient forgot (was in meeting)             │
│ → At 6 PM: System sends SMS reminder        │
│ → At 8 PM: Still not taken                  │
│ → Create Alert: 'missed_medication'         │
│ → Update: status=missed, reason=forgot      │
├─────────────────────────────────────────────┤
│ Jan 28, 8:00 PM                             │
│ Patient sees SMS, takes late dose           │
│ → Update: status=taken, taken_time=20:30   │
│ → Calculate: 150 minutes late               │
└─────────────────────────────────────────────┘

                              ↓ (Monitoring)

NURSE DASHBOARD (Day 7):
Adherence this week: 18 doses taken, 2 missed, 1 skipped
Adherence Rate = (18 + 1) / 21 * 100% = 90.5% ✅

                              ↓ (If pattern poor)

IF adherence < 70% for 3 days:
├─ Create Alert: 'low_adherence'
├─ Send SMS: "We noticed you missed doses. Everything ok?"
├─ Nurse calls patient
└─ May adjust prescription/dosing
```

---

## 4️⃣ Alert Management & Nurse Workflow

```
┌────────────────────────────────────────────────────────────────┐
│                    PATIENT ALERT LIFECYCLE                     │
└────────────────────────────────────────────────────────────────┘

STEP 1: ALERT CREATION
┌──────────────────────────────────────────┐
│ System automatically creates alerts when: │
├──────────────────────────────────────────┤
│ ✓ High-risk discharge detected           │
│ ✓ Medication dose missed (overdue)       │
│ ✓ Appointment passed & still scheduled   │
│ ✓ Vital reading abnormal                 │
│ ✓ Refill needed                          │
│ ✓ Follow-up timeframe reached            │
└──────────────────────────────────────────┘
           ↓ (Auto-assigned severity)
     Severity Level:
     • CRITICAL (red) → 5-minute SLA
     • HIGH (orange) → 10-minute SLA
     • MEDIUM (yellow) → 1-hour SLA
     • LOW (blue) → 4-hour SLA
           ↓
    STATUS: NEW (unassigned)

STEP 2: NURSE DISCOVERY
┌──────────────────────────────────────────┐
│ Nurse logs in → Sees alerts dashboard    │
├──────────────────────────────────────────┤
│ Alerts sorted by:                        │
│ 1. Severity (CRITICAL first)             │
│ 2. Time created (oldest first = urgent)  │
│ 3. SLA deadline (overdue first)          │
│                                          │
│ Nurse sees:                              │
│ ├─ ⚠️ CRITICAL - High-risk discharge     │
│ │  (3 minutes until SLA deadline)        │
│ ├─ 🟠 HIGH - Missed medication (AM)     │
│ │  (7 minutes until SLA deadline)        │
│ └─ 🟡 MEDIUM - Appointment coming up   │
│    (42 minutes until SLA deadline)       │
└──────────────────────────────────────────┘

STEP 3: ASSIGNMENT
┌──────────────────────────────────────────┐
│ Nurse clicks on HIGH alert:              │
│ "Missed medication - Aspirin AM dose"    │
├──────────────────────────────────────────┤
│ System checks:                           │
│ • Is nurse available? YES                │
│ • Current load: 8/10 patients            │
│ • Can assign? YES                        │
├──────────────────────────────────────────┤
│ Nurse clicks "Assign to Me"              │
│                                          │
│ Backend updates:                         │
│ • PatientAlert.status = 'assigned'       │
│ • PatientAlert.assigned_nurse = Nurse#5  │
│ • Create AlertLog entry (audit trail)    │
└──────────────────────────────────────────┘

STEP 4: ACTION
┌──────────────────────────────────────────┐
│ Nurse now sees patient details:          │
├──────────────────────────────────────────┤
│ ✓ Patient name: Jean Ndamyumvira         │
│ ✓ Phone: +250788123456                   │
│ ✓ Diagnosis: Diabetes                    │
│ ✓ Missed medication: Aspirin              │
│ ✓ Last dose: Yesterday 8 PM               │
│ ✓ Adherence rate: 85% this week          │
│ ✓ Previous alerts: 2 resolved             │
│                                          │
│ Nurse actions:                           │
│ 1. Calls patient                         │
│ 2. Understands: "In traffic, forgot pill"│
│ 3. Sends SMS reminder                    │
│ 4. Updates next appointment              │
│ 5. Documents conversation                │
└──────────────────────────────────────────┘

STEP 5: RESOLUTION
┌──────────────────────────────────────────┐
│ Nurse updates alert status:              │
│                                          │
│ PATCH /api/v1/nursing/alerts/{id}/resolve/
│                                          │
│ Body:                                    │
│ {                                        │
│   "resolution_notes":                    │
│     "Called patient. Emphasized importance │
│      of adherence. Patient took dose     │
│      immediately. Will set phone alarm   │
│      for next dose."                     │
│ }                                        │
├──────────────────────────────────────────┤
│ Backend updates:                         │
│ • PatientAlert.status = 'resolved'       │
│ • PatientAlert.resolved_at = NOW()       │
│ • Calculate: SLA_compliance = ON_TIME     │
│ • Create AlertLog entry                  │
│ • Update patient health metrics          │
└──────────────────────────────────────────┘

STEP 6: FOLLOW-UP
┌──────────────────────────────────────────┐
│ System monitors:                         │
│                                          │
│ • DID patient take next doses?           │
│ • If adherence returns to normal: ✅     │
│ • If poor adherence continues:           │
│   └─ Create new alert: 'low_adherence'   │
│   └─ Escalate to doctor                  │
└──────────────────────────────────────────┘
```

---

## 5️⃣ Complete Patient Discharge to Recovery Journey

```
┌────────────────────────────────────────────────────────────────┐
│                    COMPLETE PATIENT JOURNEY                    │
│         From Discharge → Recovery → Readmission Prevention     │
└────────────────────────────────────────────────────────────────┘

DAY 0: HOSPITAL DISCHARGE
├─ Hospital staff captures discharge summary
│  ├─ Diagnosis: Type 2 Diabetes (ICD-10: E11)
│  ├─ Risk: HIGH (poor glucose control)
│  ├─ Instructions (English + Kinyarwanda)
│  └─ Follow-up: 1 week with endocrinologist
│
├─ System creates prescriptions:
│  ├─ Metformin 1000mg × 2 daily × 30 days
│  ├─ Lisinopril 10mg × 1 daily × 30 days
│  └─ Aspirin 500mg × 1 daily × 30 days
│
├─ System creates appointment:
│  └─ Follow-up with Dr. Mwine (1 week)
│
└─ System creates alerts:
   ├─ 'high_risk_discharge' (severity=critical, SLA=10 min)
   ├─ 'follow_up_needed' (severity=high, SLA=24h)
   └─ 'medication_adherence' (severity=medium, SLA=4h)

DAY 0-1: NURSE CONTACTS PATIENT
├─ Nurse assigned to CRITICAL alert
├─ Calls patient same day:
│  ├─ "Hi Jean, I'm your nurse. How are you feeling?"
│  ├─ Explains medication importance
│  ├─ Sets up SMS reminder times
│  └─ "I'll text you at 8 AM, 2 PM, 8 PM for your pills"
│
└─ Alert marked RESOLVED
   └─ SLA time: 8 minutes (GOOD! Under 10-min target)

DAY 1-7: DAILY MONITORING (AUTOMATED)
├─ EACH MORNING (8 AM):
│  ├─ System generates dose schedules for today
│  ├─ If dose overdue from yesterday:
│  │  └─ Send SMS reminder: "Hi Jean, don't forget your morning pill!"
│  │
│  └─ Patient response:
│     ├─ Takes pill → App: "Dose taken at 08:15"
│     ├─ Already took → "Already taken"
│     └─ Can't take → "Skip (doctor said)"
│
├─ EACH EVENING (8 PM):
│  ├─ Check doses from morning & afternoon
│  ├─ If any dose overdue (not taken by evening):
│  │  ├─ Send SMS: "If you haven't taken your 2 PM dose, take it now"
│  │  └─ If still not taken by 10 PM:
│  │     └─ Create 'missed_medication' alert for nurse
│  │
│  └─ Nurse reviews alerts tomorrow

├─ EVERY 3 DAYS:
│  ├─ Nurse calls for check-in
│  ├─ "How are you feeling?"
│  ├─ "Any side effects from medications?"
│  └─ "On track for appointment?"
│
└─ APPOINTMENT REMINDER:
   ├─ 3 days before: SMS "Appointment in 3 days with Dr. Mwine"
   ├─ 1 day before: WhatsApp "Reminder: Tomorrow 10 AM"
   └─ Day of: SMS "Appointment in 2 hours. See you soon!"

DAY 7: FOLLOW-UP APPOINTMENT
├─ Patient attends with Dr. Mwine
├─ Doctor reviews:
│  ├─ Medication adherence: 92% (EXCELLENT!)
│  ├─ Glucose readings: Trending down (GOOD!)
│  └─ No side effects reported
├─ Doctor updates prescriptions
└─ Next appointment scheduled (2 weeks)

DAY 14-30: ONGOING MONITORING
├─ Continued daily SMS reminders
├─ Weekly nurse check-ins
├─ System tracks:
│  ├─ Medication adherence ✅ (still 88%)
│  ├─ Vital signs (patient uploads BP readings)
│  ├─ Appointments attended ✅ (2/2)
│  └─ Alerts created: 0 (CLEAN!)
│
└─ Risk score: DOWN from 75 → 35 (LOW RISK NOW!)

OUTCOMES:
┌─────────────────────────────────────────┐
│ WHAT BiCare360 PREVENTED:               │
├─────────────────────────────────────────┤
│ ✓ Medication non-adherence              │
│ ✓ Missed appointments                   │
│ ✓ Undetected complications              │
│ ✓ Hospital readmission                  │
│ ✓ Emergency room visit                  │
│                                         │
│ WHAT BiCare360 ACHIEVED:                │
│ ✓ 90%+ medication adherence             │
│ ✓ All appointments attended             │
│ ✓ Improving health metrics              │
│ ✓ Happy patient + satisfied doctor      │
│ ✓ Hospital saved $5K on avoided admit   │
└─────────────────────────────────────────┘
```

---

## 6️⃣ API Request/Response Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    TYPICAL API FLOW                            │
└────────────────────────────────────────────────────────────────┘

CLIENT REQUEST:
┌─────────────────────────────────────────┐
│ POST /api/v1/nursing/alerts/            │
│                                         │
│ Headers:                                │
│ ├─ Authorization: Bearer [JWT_TOKEN]    │
│ ├─ Content-Type: application/json       │
│ └─ Accept: application/json             │
│                                         │
│ Body:                                   │
│ {                                       │
│   "patient": 1,                         │
│   "alert_type": "missed_medication",    │
│   "severity": "high",                   │
│   "title": "Missed dose",               │
│   "description": "Patient missed 2 PM..." 
│ }                                       │
└─────────────────────────────────────────┘
                    ↓
            AUTHENTICATION CHECK
           (JWT token valid? User active?)
                    ↓
           PERMISSION CHECK
     (Is user a Nurse? Can create alerts?)
                    ↓
          SERIALIZER VALIDATION
    (Fields valid? Data types correct?)
                    ↓
           DATABASE OPERATION
┌─────────────────────────────────────────┐
│ INSERT INTO nursing_patientialert       │
│ (patient_id, alert_type, severity,      │
│  title, description, status, created_at)│
│ VALUES (1, 'missed_medication', 'high', │
│  'Missed dose', 'Patient missed 2 PM..', 
│  'new', NOW())                          │
└─────────────────────────────────────────┘
                    ↓
           RESPONSE SERIALIZATION
┌─────────────────────────────────────────┐
│ HTTP 201 Created                        │
│                                         │
│ {                                       │
│   "id": 456,                            │
│   "patient": 1,                         │
│   "alert_type": "missed_medication",    │
│   "severity": "high",                   │
│   "title": "Missed dose",               │
│   "status": "new",                      │
│   "created_at": "2026-01-28T10:30:00Z", │
│   "due_at": "2026-01-28T10:40:00Z",     │
│   "assigned_nurse": null                │
│ }                                       │
└─────────────────────────────────────────┘
                    ↓
           BACKGROUND TASKS (Celery)
├─ Send notification SMS to assigned nurse
├─ Update dashboard counter
├─ Log action in audit trail
└─ Check if SLA deadline needs escalation
```

---

## 7️⃣ User Roles & Permissions Matrix

```
┌────────────────────────────────────────────────────────────────┐
│                    ROLE-BASED ACCESS CONTROL                   │
└────────────────────────────────────────────────────────────────┘

PATIENT (Patient Portal User)
├─ Profile
│  ├─ View own profile ✅
│  ├─ View own basic info ✅
│  ├─ Edit own profile ✅
│  ├─ View other patients ❌
│  └─ Edit other patients ❌
│
├─ Appointments
│  ├─ View own appointments ✅
│  ├─ Book appointment ✅
│  ├─ Reschedule own appointment ✅
│  ├─ Cancel own appointment ✅
│  ├─ View other patient's appointments ❌
│  └─ Delete appointments ❌
│
├─ Medications
│  ├─ View own prescriptions ✅
│  ├─ Log dose (taken/missed) ✅
│  ├─ View adherence history ✅
│  ├─ View other patient's meds ❌
│  └─ Create prescriptions ❌
│
├─ Alerts
│  ├─ View own alerts ✅
│  ├─ Acknowledge alert ✅
│  ├─ Create alerts ❌
│  ├─ Assign alerts ❌
│  └─ View other patient's alerts ❌
│
└─ Vitals
   ├─ Upload vital readings ✅
   ├─ View own health trends ✅
   └─ View other patient's vitals ❌

NURSE (Healthcare Provider)
├─ Patient Management
│  ├─ View all patients ✅
│  ├─ View patient details ✅
│  ├─ Edit patient info ✅
│  ├─ Create patients ✅
│  └─ Delete patients ❌
│
├─ Alert Management
│  ├─ View all alerts ✅
│  ├─ Create alerts ✅
│  ├─ Assign alerts to self ✅
│  ├─ Assign alerts to others ✅
│  ├─ Resolve alerts ✅
│  ├─ Delete alerts ❌
│  └─ Escalate alerts ✅
│
├─ Appointments
│  ├─ View all appointments ✅
│  ├─ Create appointments ✅
│  ├─ Reschedule appointments ✅
│  ├─ Cancel appointments ✅
│  └─ Delete appointments ❌
│
├─ Medications
│  ├─ View prescriptions ✅
│  ├─ Create prescriptions ✅
│  ├─ View adherence ✅
│  ├─ Create medications ❌
│  └─ Delete prescriptions ❌
│
├─ Dashboard
│  ├─ View alerts dashboard ✅
│  ├─ View patient queue ✅
│  ├─ View performance metrics ✅
│  └─ Export reports ✅
│
└─ Workload
   ├─ Can be assigned max 10 patients ✅
   ├─ Can see current load: 8/10 ✅
   └─ Can reject overload ✅

HOSPITAL ADMIN
├─ Patient Management
│  ├─ View all hospital patients ✅
│  ├─ View discharge summaries ✅
│  ├─ Search patients ✅
│  ├─ Export patient data ✅
│  └─ Delete patients ❌
│
├─ Staff Management
│  ├─ Add nurses ✅
│  ├─ Manage nurse roles ✅
│  ├─ View nurse performance ✅
│  └─ Remove nurses ✅
│
├─ Reporting
│  ├─ View hospital analytics ✅
│  ├─ View readmission rates ✅
│  ├─ View adherence metrics ✅
│  ├─ View SLA compliance ✅
│  ├─ Export reports ✅
│  └─ Configure reports ✅
│
└─ Settings
   ├─ Configure hospital info ✅
   ├─ Set up integrations ✅
   ├─ Manage alert templates ✅
   └─ Manage message templates ✅

SYSTEM ADMIN (Superuser)
├─ Full access to everything ✅
├─ Django admin panel ✅
├─ Database management ✅
├─ User management ✅
├─ System configuration ✅
└─ Logs and monitoring ✅
```

---

## 8️⃣ Data Storage Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                         │
└────────────────────────────────────────────────────────────────┘

TABLES (13 Core + Related):

1. auth_user (Django built-in)
   ├─ username, password_hash, email, is_active
   └─ Used by: Patient + NurseProfile (OneToOne)

2. patients_patient
   ├─ user_id (ForeignKey), first_name, last_name
   ├─ national_id (UNIQUE, 16 digits), phone_number (+250...)
   └─ date_of_birth, gender, blood_type, is_active

3. patients_address
   ├─ patient_id (ForeignKey), province, district
   ├─ sector, cell, village, landmark
   └─ latitude, longitude (for field visits)

4. patients_emergencycontact
   ├─ patient_id (ForeignKey), full_name
   ├─ relationship, phone_number, is_primary
   └─ created_at

5. enrollment_hospital
   ├─ code (UNIQUE), name, hospital_type
   ├─ province, district, sector
   ├─ phone_number, email
   ├─ emr_integration_type, emr_system_name
   └─ status (active/pilot/inactive)

6. enrollment_dischargesummary
   ├─ patient_id, hospital_id, admission_date
   ├─ discharge_date, length_of_stay_days (computed)
   ├─ primary_diagnosis, icd10_primary
   ├─ secondary_diagnoses, icd10_secondary
   ├─ discharge_condition, risk_assessment
   ├─ discharge_instructions, instructions_kinyarwanda
   ├─ diet_instructions, activity_restrictions
   ├─ follow_up_required, follow_up_timeframe
   └─ created_at, updated_at

7. medications_medication
   ├─ generic_name, brand_names
   ├─ dosage_form (tablet, capsule, syrup, injection, etc)
   ├─ strength, manufacturer
   ├─ indications, contraindications, side_effects
   ├─ prescription_required, is_active
   └─ created_at

8. medications_prescription
   ├─ patient_id, medication_id, hospital_id
   ├─ discharge_summary_id (linked to discharge)
   ├─ dosage, frequency, route
   ├─ start_date, end_date, duration_days (computed)
   ├─ instructions, instructions_kinyarwanda
   ├─ refill_count, refill_notes
   └─ created_at, updated_at

9. medications_adherencelog
   ├─ prescription_id, scheduled_date, scheduled_time
   ├─ taken_date, taken_time
   ├─ status (scheduled/taken/missed/skipped/late)
   ├─ minutes_late (computed), is_overdue (computed)
   ├─ reason_missed, notes
   └─ created_at

10. appointments_appointment
    ├─ patient_id, hospital_id, discharge_summary_id
    ├─ prescription_id (for medication reviews)
    ├─ appointment_datetime, appointment_type
    ├─ status (scheduled/confirmed/completed/cancelled/no_show)
    ├─ location_type (hospital/home_visit/telemedicine)
    ├─ provider_name, department, reason
    ├─ notes, notes_kinyarwanda
    ├─ duration_minutes
    ├─ cancellation_reason, cancelled_at, cancelled_by
    └─ created_at, updated_at (INDEX: appointment_datetime)

11. appointments_appointmentreminder
    ├─ appointment_id, reminder_type (sms/whatsapp/email/call)
    ├─ scheduled_time, status (pending/sent/failed/cancelled)
    ├─ message, sent_at, failed_reason
    └─ created_at

12. nursing_nurseprofile
    ├─ user_id (OneToOne), phone_number
    ├─ license_number (UNIQUE), specialization
    ├─ current_shift, status (available/busy/on_break)
    ├─ max_concurrent_patients (default 10)
    ├─ is_active
    └─ created_at, updated_at

13. nursing_patientialert
    ├─ patient_id, alert_type (8 types)
    ├─ severity (low/medium/high/critical)
    ├─ title, description
    ├─ status (new/assigned/in_progress/resolved/escalated/closed)
    ├─ assigned_nurse_id (ForeignKey)
    ├─ created_at, due_at (created + SLA minutes)
    ├─ resolved_at, resolution_notes
    └─ created_at, updated_at (INDEX: status, created_at)

14. nursing_nursepatientassignment
    ├─ nurse_id, patient_id, alert_id
    ├─ assigned_at, status
    └─ notes

15. nursing_alertlog
    ├─ alert_id, action (created/assigned/resolved/escalated)
    ├─ nurse_id (who took action)
    ├─ duration_minutes (if resolved)
    ├─ notes
    └─ created_at

[... and more for Messaging, Consents, Vitals ...]

INDEXES (Critical for Performance):
├─ appointment_datetime (for upcoming/overdue queries)
├─ (patient_id, appointment_datetime) (patient's timeline)
├─ (status, created_at) (alert queue sorting)
├─ national_id (patient lookup)
├─ (prescription_id, status) (adherence queries)
└─ (nurse_id, status) (nurse's alert list)
```

---

## 9️⃣ Error Handling & Validation

```
┌────────────────────────────────────────────────────────────────┐
│                    VALIDATION FLOW                             │
└────────────────────────────────────────────────────────────────┘

CLIENT SENDS REQUEST:
{
  "first_name": "Jean",
  "national_id": "abc123",  ❌ INVALID (should be 16 digits)
  "phone_number": "078812345",  ❌ INVALID (missing +250)
  "date_of_birth": "invalid"  ❌ INVALID (not YYYY-MM-DD)
}

                              ↓

SERIALIZER VALIDATION:
├─ national_id: RegexValidator(r'^\d{16}$')
│  Error: "National ID must be exactly 16 digits"
│
├─ phone_number: RegexValidator(r'^\+250\d{9}$')
│  Error: "Phone must be in format: +250XXXXXXXXX"
│
└─ date_of_birth: DateField()
   Error: "Enter a valid date. Expected YYYY-MM-DD format"

                              ↓

RESPONSE:
HTTP 400 Bad Request
{
  "national_id": ["National ID must be exactly 16 digits"],
  "phone_number": ["Phone must be in format: +250XXXXXXXXX"],
  "date_of_birth": ["Enter a valid date. Expected YYYY-MM-DD format"]
}

                              ↓

CLIENT FIXES & RESUBMITS:
{
  "first_name": "Jean",
  "national_id": "1234567890123456",  ✅ VALID
  "phone_number": "+250788123456",  ✅ VALID
  "date_of_birth": "1985-05-15"  ✅ VALID
}

                              ↓

HTTP 201 Created
{
  "id": 1,
  "first_name": "Jean",
  "full_name": "Jean Ndamyumvira",
  "national_id": "1234567890123456",
  ...
}
```

---

## 🔟 Testing Coverage

```
┌────────────────────────────────────────────────────────────────┐
│                    TEST COVERAGE BY TYPE                       │
└────────────────────────────────────────────────────────────────┘

UNIT TESTS (Model & Serializer):
├─ Patient model validation
│  ├─ National ID regex
│  ├─ Phone number validation
│  ├─ Age calculation
│  └─ full_name property
│
├─ Appointment model
│  ├─ is_upcoming property
│  ├─ is_overdue property
│  └─ Auto-indexing
│
├─ PatientAlert model
│  ├─ SLA deadline calculation
│  ├─ Severity assignment
│  └─ Auto-audit logging
│
└─ Serializers
   ├─ Input validation
   ├─ Output formatting
   └─ Nested serialization

INTEGRATION TESTS (API Endpoints):
├─ POST /api/v1/patients/ - Create with validation
├─ GET /api/v1/patients/?search=name - Search filtering
├─ PATCH /api/v1/appointments/{id}/reschedule/ - Complex update
├─ POST /api/v1/nursing/alerts/ - With permissions
└─ GET /api/v1/nursing/alerts/?severity=critical - Filtering

PERMISSION TESTS:
├─ Unauthenticated request → 401 Unauthorized
├─ Patient accessing other patient → 403 Forbidden
├─ Non-nurse creating alert → 403 Forbidden
├─ Nurse at capacity → 400 Bad Request
└─ Proper JWT token → 200 OK

EDGE CASE TESTS:
├─ Birth date in future → Error
├─ Appointment in past → Marked overdue
├─ Prescription end date passed → Not current
├─ Adherence < 0% → Capped at 0
├─ National ID with spaces → Stripped
├─ Phone number with dashes → Normalized
└─ Empty string values → Handled gracefully

CURRENT COVERAGE:
├─ Patients: 131 tests, 100% coverage ✅
├─ Enrollment: 54 tests, 98% coverage ✅
├─ Medications: ~50 tests, 95% coverage ✅
├─ Appointments: 25 tests, 100% coverage ✅
├─ Nursing: ~40 tests, 95% coverage ✅
├─ Consents: ~30 tests, 95% coverage ✅
├─ Messaging: ~40 tests, 90% coverage 🔄
└─ TOTAL: 511 tests, 81.44% coverage ✅
```

---

## 1️⃣1️⃣ Performance Optimization

```
┌────────────────────────────────────────────────────────────────┐
│                    OPTIMIZATION STRATEGIES                     │
└────────────────────────────────────────────────────────────────┘

DATABASE OPTIMIZATION:
├─ Indexes on frequently queried columns
│  ├─ appointment_datetime (for upcoming queries)
│  ├─ status (for alert dashboard)
│  └─ patient_id (foreign key lookups)
│
├─ Select_related for ForeignKey lookups
│  └─ get patient.hospital (avoid N+1)
│
├─ Prefetch_related for reverse FK
│  └─ get all appointments for patient in 1 query
│
└─ Database query caching
   └─ Cache alert lists for 30 seconds

CACHING STRATEGY:
├─ Patient profile (30 min)
├─ Medication catalog (24 hours)
├─ Hospital list (24 hours)
├─ Appointment reminders (1 hour)
└─ Nurse availability (5 minutes)

ASYNC OPERATIONS (Celery):
├─ Send SMS/WhatsApp (background task)
├─ Send emails (background task)
├─ Generate daily adherence logs (nightly 11 PM)
├─ Check overdue doses (hourly 11 AM + 6 PM)
├─ Calculate risk scores (daily 9 AM)
└─ Generate reports (nightly)

API PAGINATION:
├─ Default page size: 20 items
├─ Max page size: 100 items
├─ Cursor-based pagination for large datasets

FRONTEND OPTIMIZATION:
├─ React Query caching (5 min default)
├─ Lazy loading of routes
├─ Image optimization
├─ Bundle code splitting
└─ Service Worker for offline support
```

---

This architecture document provides the complete visual overview of how BiCare360 works. Combine it with [CODEBASE_INDEX.md](CODEBASE_INDEX.md) and [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for comprehensive understanding.

