# BiCare360 System Architecture - Visual Guide

## 🏛️ HIGH-LEVEL SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BICARE360 PLATFORM                          │
│                    Post-Discharge Care Coordination                 │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   HOSPITAL       │────▶│   BICARE360      │◀────│   PATIENT        │
│   STAFF          │     │   BACKEND        │     │   (Home)         │
│                  │     │                  │     │                  │
│ • Doctors        │     │ • Django REST    │     │ • SMS/WhatsApp   │
│ • Nurses         │     │ • PostgreSQL     │     │ • Patient Portal │
│ • Discharge      │     │ • Celery/Redis   │     │ • Mobile App     │
│   Coordinators   │     │ • JWT Auth       │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                         │
         │                        │                         │
         ▼                        ▼                         ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   ADMIN          │     │   NURSE          │     │   CARE GUIDE     │
│   DASHBOARD      │     │   TRIAGE         │     │   (Abafasha)     │
│                  │     │   CONSOLE        │     │                  │
│ • Analytics      │     │ • Alert Queue    │     │ • Home Visits    │
│ • Reports        │     │ • Patient List   │     │ • GPS Nav        │
│ • User Mgmt      │     │ • SLA Tracking   │     │ • Feedback       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## 🗄️ DATABASE SCHEMA (Entity Relationship)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CORE ENTITIES                               │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Hospital   │
    │──────────────│
    │ id           │
    │ name         │
    │ code         │◀──────────┐
    │ type         │           │
    │ province     │           │
    │ district     │           │
    └──────────────┘           │
                               │
                               │ FK
    ┌──────────────┐           │
    │   Patient    │           │
    │──────────────│           │
    │ id           │◀──────┐   │
    │ national_id  │       │   │
    │ first_name   │       │   │
    │ phone_number │       │   │
    │ user_id (FK) │       │   │
    └──────────────┘       │   │
         │                 │   │
         │ 1:1             │   │
         ▼                 │   │
    ┌──────────────┐       │   │
    │   Address    │       │   │
    │──────────────│       │   │
    │ patient_id   │       │   │
    │ province     │       │   │
    │ district     │       │   │
    │ sector       │       │   │
    │ cell         │       │   │
    │ village      │       │   │
    │ latitude     │       │   │
    │ longitude    │       │   │
    └──────────────┘       │   │
                           │   │
                           │   │
    ┌──────────────────────┴───┴──┐
    │   DischargeSummary          │
    │─────────────────────────────│
    │ id                          │
    │ patient_id (FK)             │
    │ hospital_id (FK)            │
    │ admission_date              │
    │ discharge_date              │
    │ primary_diagnosis           │
    │ risk_level                  │◀────────┐
    │ follow_up_required          │         │
    └─────────────────────────────┘         │
         │                                   │
         │ 1:N                               │
         ▼                                   │
    ┌──────────────────────────────┐        │
    │   Prescription               │        │
    │──────────────────────────────│        │
    │ id                           │        │
    │ patient_id (FK)              │        │
    │ discharge_summary_id (FK)    │        │
    │ medication_id (FK)           │        │
    │ dosage                       │        │
    │ frequency_times_per_day      │        │
    │ start_date                   │        │
    │ end_date                     │        │
    └──────────────────────────────┘        │
         │                                   │
         │ 1:N                               │
         ▼                                   │
    ┌──────────────────────────────┐        │
    │   MedicationAdherence        │        │
    │──────────────────────────────│        │
    │ id                           │        │
    │ prescription_id (FK)         │        │
    │ patient_id (FK)              │        │
    │ scheduled_date               │        │
    │ scheduled_time               │        │
    │ status (scheduled/taken)     │        │
    │ taken_at                     │        │
    │ reminder_sent                │        │
    └──────────────────────────────┘        │
                                             │
                                             │
    ┌──────────────────────────────┐        │
    │   Appointment                │        │
    │──────────────────────────────│        │
    │ id                           │        │
    │ patient_id (FK)              │        │
    │ hospital_id (FK)             │        │
    │ discharge_summary_id (FK)    │        │
    │ appointment_datetime         │        │
    │ appointment_type             │        │
    │ status                       │        │
    └──────────────────────────────┘        │
         │                                   │
         │ 1:N                               │
         ▼                                   │
    ┌──────────────────────────────┐        │
    │   AppointmentReminder        │        │
    │──────────────────────────────│        │
    │ id                           │        │
    │ appointment_id (FK)          │        │
    │ reminder_datetime            │        │
    │ reminder_type (sms/whatsapp) │        │
    │ status                       │        │
    └──────────────────────────────┘        │
                                             │
                                             │
    ┌──────────────────────────────┐        │
    │   PatientAlert               │◀───────┘
    │──────────────────────────────│
    │ id                           │
    │ patient_id (FK)              │
    │ discharge_summary_id (FK)    │
    │ assigned_nurse_id (FK)       │
    │ alert_type                   │
    │ severity                     │
    │ status                       │
    │ sla_deadline                 │
    │ created_at                   │
    │ acknowledged_at              │
    │ resolved_at                  │
    └──────────────────────────────┘
         │
         │ FK
         ▼
    ┌──────────────────────────────┐
    │   NurseProfile               │
    │──────────────────────────────│
    │ id                           │
    │ user_id (FK)                 │
    │ license_number               │
    │ current_shift                │
    │ status                       │
    │ max_concurrent_patients      │
    └──────────────────────────────┘
```

---

## 🔄 DATA FLOW: PATIENT DISCHARGE TO HOME CARE

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: HOSPITAL DISCHARGE                                          │
└─────────────────────────────────────────────────────────────────────┘

Hospital Staff                BiCare360 Backend
     │                              │
     │  POST /discharge-summaries   │
     ├─────────────────────────────▶│
     │  {                           │
     │    patient_id: 123,          │
     │    risk_level: "high",       │
     │    diagnoses: "...",         │
     │    prescriptions: [...]      │
     │  }                           │
     │                              │
     │                              ├─ Create DischargeSummary
     │                              ├─ Create Prescriptions (3 meds)
     │                              ├─ Create Appointments (follow-up)
     │                              └─ Create AppointmentReminders
     │                              │
     │  201 Created                 │
     │◀─────────────────────────────┤
     │                              │

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: ALERT ENGINE (Runs every 10 minutes via Celery)            │
└─────────────────────────────────────────────────────────────────────┘

Celery Beat Scheduler          Alert Engine                Database
     │                              │                          │
     │  Trigger: run_alert_engine   │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              │  Query high-risk         │
     │                              │  discharge summaries     │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              │  DischargeSummary        │
     │                              │  (risk_level='high')     │
     │                              │◀─────────────────────────┤
     │                              │                          │
     │                              ├─ Create PatientAlert     │
     │                              │  (severity='high',       │
     │                              │   sla_deadline=30min)    │
     │                              │                          │
     │                              ├─ Find available nurse    │
     │                              ├─ Assign alert to nurse   │
     │                              │                          │
     │                              │  Save PatientAlert       │
     │                              ├─────────────────────────▶│
     │                              │                          │

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: MEDICATION ADHERENCE TRACKING                               │
└─────────────────────────────────────────────────────────────────────┘

Celery Task                    Database                  SMS Service
     │                              │                          │
     │  Create adherence records    │                          │
     │  for today's doses           │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  MedicationAdherence         │                          │
     │  (scheduled_time=08:00)      │                          │
     │  (scheduled_time=20:00)      │                          │
     │                              │                          │
     │                              │                          │
     │  1 hour before dose (07:00)  │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  Find adherence records      │                          │
     │  where scheduled_time - 1hr  │                          │
     │  = now                       │                          │
     │                              │                          │
     │  Send SMS reminder           │                          │
     ├──────────────────────────────┼─────────────────────────▶│
     │                              │                          │
     │                              │  Africa's Talking API    │
     │                              │  POST /sms/send          │
     │                              │                          ├─┐
     │                              │                          │ │
     │                              │                          │ │ Send SMS
     │                              │                          │ │ to patient
     │                              │                          │◀┘
     │                              │                          │
     │  Update reminder_sent=True   │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: MISSED DOSE DETECTION                                       │
└─────────────────────────────────────────────────────────────────────┘

Alert Engine                   Database                  Nurse Console
     │                              │                          │
     │  Check for overdue doses     │                          │
     │  (scheduled_time passed,     │                          │
     │   status='scheduled')        │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  MedicationAdherence         │                          │
     │  (is_overdue=True)           │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │
     │  Create PatientAlert         │                          │
     │  (type='missed_medication',  │                          │
     │   severity='medium')         │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  Assign to nurse             │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              │  Notify nurse            │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              │  Alert appears in queue  │
     │                              │                          │

┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: NURSE INTERVENTION                                          │
└─────────────────────────────────────────────────────────────────────┘

Nurse Console                  Backend API               Patient
     │                              │                          │
     │  GET /alerts?status=new      │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  List of alerts              │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │
     │  PATCH /alerts/456           │                          │
     │  {status: "in_progress"}     │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  (Nurse calls patient)       │                          │
     ├──────────────────────────────┼─────────────────────────▶│
     │                              │                          │
     │                              │  "Did you take your      │
     │                              │   medication?"           │
     │                              │                          │
     │                              │  "Yes, I took it late"   │
     │◀─────────────────────────────┼──────────────────────────┤
     │                              │                          │
     │  PATCH /adherence/789        │                          │
     │  {status: "late",            │                          │
     │   taken_at: "2025-01-15..."}│                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  PATCH /alerts/456           │                          │
     │  {status: "resolved"}        │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
```

---

## 🔐 AUTHENTICATION & AUTHORIZATION FLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│ PATIENT REGISTRATION & LOGIN                                        │
└─────────────────────────────────────────────────────────────────────┘

Patient Portal                 Backend API               Database
     │                              │                          │
     │  POST /patients/register/    │                          │
     ├─────────────────────────────▶│                          │
     │  {                           │                          │
     │    username: "john_doe",     │                          │
     │    password: "secure123",    │                          │
     │    national_id: "...",       │                          │
     │    first_name: "John",       │                          │
     │    ...                       │                          │
     │  }                           │                          │
     │                              │                          │
     │                              ├─ Validate data          │
     │                              ├─ Create User            │
     │                              ├─ Create Patient         │
     │                              ├─ Link User ↔ Patient    │
     │                              │                          │
     │                              │  Save User & Patient     │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              ├─ Generate JWT tokens    │
     │                              │  (access + refresh)      │
     │                              │                          │
     │  201 Created                 │                          │
     │  {                           │                          │
     │    patient: {...},           │                          │
     │    tokens: {                 │                          │
     │      access: "eyJ...",       │                          │
     │      refresh: "eyJ..."       │                          │
     │    }                         │                          │
     │  }                           │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │
     │  Store tokens in localStorage│                          │
     │                              │                          │
     │                              │                          │
     │  GET /patients/me/           │                          │
     │  Header: Authorization:      │                          │
     │    Bearer eyJ...             │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              ├─ Verify JWT signature   │
     │                              ├─ Extract user_id        │
     │                              ├─ Load request.user      │
     │                              │                          │
     │                              │  Query Patient           │
     │                              │  WHERE user_id=...       │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              │  Patient data            │
     │                              │◀─────────────────────────┤
     │                              │                          │
     │  200 OK                      │                          │
     │  {patient data}              │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │

┌─────────────────────────────────────────────────────────────────────┐
│ PERMISSION CHECKS                                                   │
└─────────────────────────────────────────────────────────────────────┘

Request                        Permission Class          Decision
     │                              │                          │
     │  GET /patients/123/          │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              ├─ Check IsAuthenticated  │
     │                              │  ✓ User logged in        │
     │                              │                          │
     │                              ├─ Check IsPatientOrAdmin │
     │                              │  • Is admin? No          │
     │                              │  • Is patient? Yes       │
     │                              │  • Is own data? Check... │
     │                              │    patient.id == 123?    │
     │                              │    ✓ Yes, allow          │
     │                              │                          │
     │  Allow request               │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │
```

---

## 📨 MESSAGING SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│ SMS/WHATSAPP MESSAGE FLOW                                           │
└─────────────────────────────────────────────────────────────────────┘

Trigger Event                  Message Service           Africa's Talking
     │                              │                          │
     │  Appointment reminder due    │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              ├─ Load MessageTemplate   │
     │                              │  (appointment_reminder)  │
     │                              │                          │
     │                              ├─ Render template        │
     │                              │  Replace {patient_name}, │
     │                              │  {appointment_date}, etc.│
     │                              │                          │
     │                              ├─ Create Message record  │
     │                              │  (status='pending')      │
     │                              │                          │
     │                              ├─ Add to MessageQueue    │
     │                              │  (priority='normal')     │
     │                              │                          │
     │                              │                          │
Celery Worker                       │                          │
     │                              │                          │
     │  Process queue               │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              ├─ Get pending messages   │
     │                              │  WHERE scheduled_time    │
     │                              │  <= now                  │
     │                              │                          │
     │                              ├─ Call SMSService        │
     │                              │                          │
     │                              │  POST /sms/send          │
     │                              ├─────────────────────────▶│
     │                              │  {                       │
     │                              │    to: "+250788...",     │
     │                              │    message: "Muraho..."  │
     │                              │  }                       │
     │                              │                          │
     │                              │  Response:               │
     │                              │  {                       │
     │                              │    status: "Success",    │
     │                              │    messageId: "AT123",   │
     │                              │    cost: "0.05 USD"      │
     │                              │  }                       │
     │                              │◀─────────────────────────┤
     │                              │                          │
     │                              ├─ Update Message         │
     │                              │  (status='sent')         │
     │                              │                          │
     │                              ├─ Create MessageLog      │
     │                              │  (provider_message_id,   │
     │                              │   cost, timestamp)       │
     │                              │                          │
     │                              ├─ Update MessageQueue    │
     │                              │  (status='completed')    │
     │                              │                          │
```

---

## 🚨 ALERT ENGINE WORKFLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│ ALERT CREATION & ASSIGNMENT                                         │
└─────────────────────────────────────────────────────────────────────┘

Alert Engine                   Database                  Nurse Assignment
     │                              │                          │
     │  Run all checks              │                          │
     │  ├─ High-risk discharges     │                          │
     │  ├─ Missed medications       │                          │
     │  ├─ Missed appointments      │                          │
     │  └─ Symptom reports          │                          │
     │                              │                          │
     │  Query: DischargeSummary     │                          │
     │  WHERE risk_level IN         │                          │
     │    ('high', 'critical')      │                          │
     │  AND days_since_discharge<=7 │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  Results: 3 high-risk        │                          │
     │  patients                    │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │
     │  For each patient:           │                          │
     │  ├─ Check if alert exists    │                          │
     │  ├─ If not, create alert     │                          │
     │  │                            │                          │
     │  Create PatientAlert         │                          │
     │  ├─ severity = 'high'        │                          │
     │  ├─ sla_deadline = now+30min │                          │
     │  └─ status = 'new'           │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  Find available nurse        │                          │
     │  WHERE status='available'    │                          │
     │  AND current_patient_count   │                          │
     │    < max_concurrent_patients │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  NurseProfile (Nurse A)      │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │
     │  Assign alert to Nurse A     │                          │
     │  ├─ assigned_nurse_id        │                          │
     │  ├─ assigned_at = now        │                          │
     │  └─ status = 'assigned'      │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  Create AlertLog             │                          │
     │  (action='assigned')         │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              │  Notify Nurse A          │
     │                              ├─────────────────────────▶│
     │                              │  (WebSocket/Push)        │
     │                              │                          │

┌─────────────────────────────────────────────────────────────────────┐
│ SLA MONITORING & ESCALATION                                         │
└─────────────────────────────────────────────────────────────────────┘

Alert Engine                   Database                  Escalation
     │                              │                          │
     │  Check overdue alerts        │                          │
     │  WHERE sla_deadline < now    │                          │
     │  AND status NOT IN           │                          │
     │    ('resolved', 'closed')    │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  PatientAlert (overdue)      │                          │
     │◀─────────────────────────────┤                          │
     │                              │                          │
     │  Update alert                │                          │
     │  ├─ status = 'escalated'     │                          │
     │  └─ escalation_reason =      │                          │
     │      "SLA breach: 45 min"    │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │  Create AlertLog             │                          │
     │  (action='escalated')        │                          │
     ├─────────────────────────────▶│                          │
     │                              │                          │
     │                              │  Notify supervisor       │
     │                              ├─────────────────────────▶│
     │                              │  Send email/SMS          │
     │                              │                          │
```

---

## 🔄 CELERY TASK SCHEDULING

```
┌─────────────────────────────────────────────────────────────────────┐
│ PERIODIC TASK EXECUTION                                             │
└─────────────────────────────────────────────────────────────────────┘

Celery Beat                    Celery Workers            Tasks
     │                              │                          │
     │  Every 5 minutes             │                          │
     ├─────────────────────────────▶│                          │
     │                              │  process_message_queue() │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              │  ├─ Get pending messages │
     │                              │  ├─ Send via SMS service │
     │                              │  └─ Update status        │
     │                              │                          │
     │                              │                          │
     │  Every 10 minutes            │                          │
     ├─────────────────────────────▶│                          │
     │                              │  run_alert_engine()      │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              │  ├─ Check high-risk      │
     │                              │  ├─ Check missed meds    │
     │                              │  ├─ Check missed appts   │
     │                              │  ├─ Create alerts        │
     │                              │  └─ Assign to nurses     │
     │                              │                          │
     │                              │                          │
     │  Every hour                  │                          │
     ├─────────────────────────────▶│                          │
     │                              │  send_appointment_       │
     │                              │  reminders()             │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              │  ├─ Find due reminders   │
     │                              │  ├─ Render templates     │
     │                              │  └─ Queue messages       │
     │                              │                          │
     │                              │                          │
     │  Daily at midnight           │                          │
     ├─────────────────────────────▶│                          │
     │                              │  generate_adherence_     │
     │                              │  records()               │
     │                              ├─────────────────────────▶│
     │                              │                          │
     │                              │  ├─ Get active Rx        │
     │                              │  ├─ Create adherence     │
     │                              │  │  records for tomorrow │
     │                              │  └─ Schedule reminders   │
     │                              │                          │
```

---

**End of Visual Architecture Guide**
