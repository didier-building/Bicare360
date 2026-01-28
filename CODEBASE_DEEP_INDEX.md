# BiCare360 Codebase Deep Index

**Generated:** 2025  
**Purpose:** Complete understanding of every line of code and architectural intent

---

## 🎯 PROBLEM STATEMENT

### Core Healthcare Gap in Rwanda
**Problem:** Patients discharged from hospitals face a "care cliff" - they leave with prescriptions and instructions but have minimal support at home, leading to:
- Medication non-adherence (patients forget or stop taking meds)
- Missed follow-up appointments
- Preventable hospital readmissions
- Poor health outcomes
- Increased healthcare costs

**BiCare360 Solution:** A "Hybrid Care Bridge" that combines:
1. **Digital automation** (SMS/WhatsApp reminders, AI chatbot)
2. **Human care coordination** (nurse triage, care guide home visits)
3. **Data-driven insights** (risk assessment, adherence tracking)

---

## 🏗️ SYSTEM ARCHITECTURE

### Technology Stack
```
Backend:  Django 4.2.9 + DRF 3.14.0 + PostgreSQL 15+
Auth:     JWT (Simple JWT) - Token-based authentication
Queue:    Celery 5.3.6 + Redis 7+ (async task processing)
SMS:      Africa's Talking API (Rwanda SMS/WhatsApp)
Frontend: React 18+ + TypeScript + Vite (in development)
Mobile:   React Native + Expo (planned)
```

### Database Design Philosophy
- **Relational integrity:** Foreign keys with PROTECT/CASCADE
- **Audit trails:** created_at, updated_at on all models
- **Soft deletes:** is_active flags instead of hard deletes
- **Bilingual support:** English + Kinyarwanda fields
- **Rwanda-specific:** National ID (16 digits), phone (+250), admin structure

---

## 📦 APPLICATION MODULES

### 1. **apps/patients/** - Patient Management
**Purpose:** Core patient enrollment and demographic data

#### Models (models.py)
```python
Patient:
  - Links to Django User (OneToOne) for portal authentication
  - Rwanda national_id: 16 digits, unique, regex validated
  - Phone: +250XXXXXXXXX format (Rwanda country code)
  - Bilingual names: first_name_kinyarwanda, last_name_kinyarwanda
  - Communication prefs: prefers_sms, prefers_whatsapp, language_preference
  - Medical: blood_type, date_of_birth
  - Metadata: is_active, enrolled_date, enrolled_by (staff user)
  - Computed: full_name, age (calculated from DOB)

Address:
  - OneToOne with Patient
  - Rwanda admin structure: province → district → sector → cell → village
  - GPS coordinates: latitude, longitude (for care guide field visits)
  - Landmarks: text field for navigation help

EmergencyContact:
  - ForeignKey to Patient (one patient, many contacts)
  - Relationship choices: parent, spouse, child, sibling, friend, other
  - is_primary flag for main contact
```

#### Views (views.py)
```python
PatientViewSet:
  - CRUD operations with JWT authentication
  - Custom actions:
    • /me/ - Get/update current patient (from JWT token)
    • /change_password/ - Password change
    • /search/ - Advanced search (full-text, filters, sorting)
    • /stats/ - Patient statistics dashboard
    • /export_data/ - GDPR data portability
    • /request_deletion/ - GDPR right to erasure
    • /deactivate/, /activate/ - Soft delete/restore

patient_register():
  - AllowAny permission (public endpoint)
  - Creates User + Patient in one transaction
  - Returns JWT tokens for immediate login

patient_login():
  - Authenticates by username OR national_id
  - Returns JWT tokens + patient data
  - Checks is_active status

request_appointment():
  - Authenticated patients can request appointments
  - Creates Appointment with 'scheduled' status
```

**Intent:** Patients are the central entity. Every other module references Patient. The system supports both staff-enrolled patients (hospital discharge) and self-registered patients (portal access).

---

### 2. **apps/enrollment/** - Hospital & Discharge Management
**Purpose:** Track hospitals and capture comprehensive discharge summaries

#### Models (models.py)
```python
Hospital:
  - Unique code: e.g., CHUK, KFH
  - Types: referral, district, health_center, clinic
  - Location: province, district, sector (Rwanda structure)
  - EMR integration: manual, api, hl7
  - Status: active, pilot, inactive

DischargeSummary:
  - ForeignKey to Patient, Hospital
  - Dates: admission_date, discharge_date
  - Auto-calculated: length_of_stay_days (in save() method)
  - Diagnoses: primary_diagnosis, secondary_diagnoses
  - ICD-10 codes: icd10_primary, icd10_secondary (for analytics)
  - Treatment: procedures_performed, treatment_summary
  - Discharge: condition (improved/stable/unchanged/deteriorated)
  - Instructions: bilingual (English + Kinyarwanda)
  - Risk assessment: risk_level (low/medium/high/critical)
  - Follow-up: follow_up_required, follow_up_timeframe, follow_up_with
  - Warning signs: bilingual symptoms requiring immediate attention
  - Providers: attending_physician, discharge_nurse
  - Computed properties:
    • is_high_risk: True if risk_level in ['high', 'critical']
    • days_since_discharge: Days elapsed since discharge
```

**Intent:** DischargeSummary is the "handoff document" from hospital to home care. It contains everything needed for post-discharge care coordination. Risk level drives alert priority in nursing module.

---

### 3. **apps/medications/** - Medication Management
**Purpose:** Medication catalog, prescriptions, and adherence tracking

#### Models (models.py)
```python
Medication:
  - Catalog of available medications in Rwanda
  - Dosage forms: tablet, capsule, syrup, injection, cream, ointment, drops, inhaler, patch, suppository
  - Fields: name, generic_name, brand_name, strength, manufacturer
  - Medical info: indication, contraindications, side_effects
  - requires_prescription flag
  - is_active flag (for discontinued meds)

Prescription:
  - ForeignKey to Patient, Medication, DischargeSummary (optional)
  - Dosage details: dosage, frequency, frequency_times_per_day, route, duration_days
  - Bilingual instructions: instructions, instructions_kinyarwanda
  - Dates: start_date, end_date
  - Refills: refills_allowed, refills_remaining
  - Computed properties:
    • is_current: Active and within date range
    • days_remaining: Days until end_date

MedicationAdherence:
  - ForeignKey to Prescription, Patient
  - Scheduling: scheduled_date, scheduled_time
  - Status: scheduled, taken, missed, skipped, late
  - Tracking: taken_at (actual time), reason_missed
  - Reminders: reminder_sent, reminder_sent_at
  - Unique constraint: (prescription, scheduled_date, scheduled_time)
  - Computed properties:
    • is_overdue: scheduled_time passed but status still 'scheduled'
    • minutes_late: If status='late', calculates delay

PatientMedicationTracker:
  - Daily check-in tracking
  - Status: taken, missed, delayed, not_reported
  - Unique: (patient, prescription, date)

SymptomReport:
  - Patient-reported symptoms/side effects
  - Severity: mild, moderate, severe, critical
  - Types: side_effect, symptom, pain, fatigue, nausea, dizziness, other
  - Nurse review: reviewed_by_nurse, nurse_response, reviewed_at

PrescriptionRefillRequest:
  - Patient requests refills
  - Status: pending, approved, denied, completed
  - urgent flag for priority handling
```

**Intent:** Medications are prescribed at discharge. Adherence records are created for each scheduled dose. SMS reminders are sent before scheduled_time. Missed doses trigger alerts to nurses. This is the core of preventing readmissions.

---

### 4. **apps/appointments/** - Appointment Scheduling
**Purpose:** Schedule and track follow-up appointments with reminders

#### Models (models.py)
```python
Appointment:
  - ForeignKey to Patient, Hospital, DischargeSummary (optional), Prescription (optional)
  - appointment_datetime: When appointment occurs
  - Types: follow_up, medication_review, consultation, emergency, routine_checkup
  - Status: scheduled, confirmed, completed, cancelled, no_show, rescheduled
  - Location: hospital, home_visit, telemedicine
  - Provider: provider_name, department
  - Bilingual notes: notes, notes_kinyarwanda
  - Cancellation tracking: cancellation_reason, cancelled_at, cancelled_by
  - Computed properties:
    • is_upcoming: appointment_datetime > now
    • is_overdue: Past datetime but still scheduled/confirmed

AppointmentReminder:
  - ForeignKey to Appointment
  - reminder_datetime: When to send reminder
  - Types: sms, whatsapp, email, call
  - Status: pending, sent, failed, cancelled
  - Bilingual messages: message, message_kinyarwanda
  - Delivery tracking: sent_at, error_message
  - Computed: is_due (reminder_datetime <= now and status='pending')
```

**Intent:** Appointments are created from discharge summaries (follow-up required). Reminders are scheduled automatically (e.g., 24 hours before, 1 hour before). Celery tasks process pending reminders.

---

### 5. **apps/consents/** - GDPR Compliance
**Purpose:** Track patient consent and privacy preferences

#### Models (models.py)
```python
ConsentVersion:
  - Version control for consent text
  - Types: data_processing, marketing, research, data_sharing
  - version_number: e.g., "1.0", "2.0"
  - Bilingual content: content_english, content_kinyarwanda
  - effective_date: When version becomes active
  - is_active flag

Consent:
  - ForeignKey to Patient, ConsentVersion
  - granted: True/False (consent given or revoked)
  - granted_date, revoked_date
  - ip_address: Audit trail
  - Computed: is_active (granted and not revoked)

PrivacyPreference:
  - OneToOne with Patient
  - Flags: allow_data_export, allow_marketing_communications, allow_research_participation, allow_third_party_sharing
  - preferred_contact_method: email, sms, whatsapp, phone, none

ConsentAuditLog:
  - ForeignKey to Consent
  - Actions: granted, revoked, updated, viewed, exported
  - performed_by: user/system/patient/admin
  - timestamp, details, ip_address
```

**Intent:** GDPR compliance for Rwanda's data protection laws. Every consent action is logged. Patients can export data (/export_data/) or request deletion (/request_deletion/).

---

### 6. **apps/messaging/** - SMS/WhatsApp Communication
**Purpose:** Message queue and delivery tracking via Africa's Talking

#### Models (models.py)
```python
MessageTemplate:
  - Reusable message templates
  - Types: appointment_reminder, medication_reminder, general_notification, emergency_alert, survey
  - Message types: sms, whatsapp
  - Bilingual content with placeholders: {patient_name}, {appointment_date}, etc.
  - is_active flag

Message:
  - ForeignKey to Patient (recipient_patient), Appointment (optional), MessageTemplate (optional)
  - recipient_phone: +250XXXXXXXXX
  - content: Rendered message (template + variables)
  - Status: pending, queued, sent, delivered, failed, cancelled
  - Scheduling: scheduled_send_time, sent_at

MessageLog:
  - ForeignKey to Message
  - Detailed delivery tracking
  - provider_message_id: Africa's Talking message ID
  - provider_response: Full API response
  - error_message: If failed
  - cost, currency: Billing tracking

MessageQueue:
  - Queue for scheduled messages
  - Priority: low, normal, high, urgent
  - Retry logic: retry_count, max_retries
  - Status: pending, processing, completed, failed, cancelled
  - context_data: JSON field for template variables
```

**Services (services.py, sms_service.py, mock_sms_service.py):**
```python
MessageService:
  - send_message(): Main entry point
  - send_appointment_reminder()
  - send_medication_reminder()
  - Uses SMSService or MockSMSService based on SMS_DEMO_MODE

SMSService:
  - Africa's Talking integration
  - send_sms(): Actual API call
  - Handles API responses, logs delivery

MockSMSService:
  - Development/testing mode
  - Simulates SMS sending without API calls
  - Logs to console
```

**Tasks (tasks.py):**
```python
@shared_task
process_message_queue():
  - Celery periodic task
  - Finds pending messages where scheduled_time <= now
  - Sends via MessageService
  - Updates status and logs

@shared_task
send_appointment_reminders():
  - Finds appointments with pending reminders
  - Creates Message and sends
```

**Intent:** Centralized messaging system. All SMS/WhatsApp go through this module. Africa's Talking API is abstracted behind service layer. Mock mode for development. Celery handles async sending.

---

### 7. **apps/nursing/** - Nurse Triage & Alert System
**Purpose:** Alert engine for patient issues requiring nurse intervention

#### Models (models.py)
```python
NurseProfile:
  - OneToOne with Django User
  - license_number: Unique nurse identifier
  - Shifts: morning (6AM-2PM), afternoon (2PM-10PM), night (10PM-6AM)
  - Status: available, busy, on_break, off_duty
  - max_concurrent_patients: Workload limit
  - Computed:
    • current_patient_count: Active assignments
    • is_available_for_assignment: Can take more patients

PatientAlert:
  - ForeignKey to Patient, NurseProfile (assigned_nurse), DischargeSummary, Appointment
  - Types: missed_medication, missed_appointment, high_risk_discharge, symptom_report, readmission_risk, medication_side_effect, emergency, follow_up_needed
  - Severity: low, medium, high, critical
  - Status: new, assigned, in_progress, resolved, escalated, closed
  - SLA tracking: created_at, acknowledged_at, resolved_at, sla_deadline
  - Auto-calculated SLA in save():
    • critical: 10 minutes
    • high: 30 minutes
    • medium: 120 minutes
    • low: 240 minutes
  - Computed properties:
    • is_overdue: Now > sla_deadline and not resolved
    • response_time_minutes: acknowledged_at - created_at
    • resolution_time_minutes: resolved_at - created_at

NursePatientAssignment:
  - ForeignKey to NurseProfile, Patient, DischargeSummary
  - Status: active, pending, completed, transferred
  - priority: Integer (higher = more urgent)
  - last_contact_at: Track nurse-patient communication

AlertLog:
  - ForeignKey to PatientAlert
  - Actions: created, assigned, acknowledged, updated, resolved, escalated, closed
  - Audit trail: performed_by, notes, timestamp
```

**Alert Engine (alert_engine.py):**
```python
AlertEngine:
  - check_high_risk_discharges(): Creates alerts for high/critical risk patients
  - check_missed_medications(): Scans overdue adherence records
  - check_missed_appointments(): Finds overdue appointments
  - check_symptom_reports(): Alerts for severe symptoms
  - assign_alert_to_nurse(): Auto-assigns to available nurse
  - escalate_overdue_alerts(): Escalates if SLA breached
  - run_all_checks(): Main entry point
```

**Management Command (management/commands/run_alert_engine.py):**
```bash
python manage.py run_alert_engine
```
Runs all alert checks. Called by Celery periodic task.

**Intent:** Proactive monitoring. Alert engine runs every 5-10 minutes. High-risk patients get immediate alerts. Nurses have 10-minute SLA for critical alerts. This prevents patients from "falling through the cracks."

---

### 8. **apps/core/** - Shared Utilities
**Purpose:** Cross-cutting concerns like permissions

#### Permissions (permissions.py)
```python
IsAuthenticatedUser: Base authentication check
IsPatient: User has Patient profile
IsProvider: User has Provider profile (future)
IsAdmin: User is staff
IsOwnerOrAdmin: Object owner or admin
IsPatientOrAdmin: Patient (own data) or admin
IsProviderOrAdmin: Provider (their patients) or admin
IsNurse: User has NurseProfile
IsNurseOrAdmin: Nurse or admin
```

**Intent:** Role-based access control (RBAC). Patients see only their data. Nurses see assigned patients. Admins see everything. Applied via `permission_classes` in ViewSets.

---

### 9. **apps/users/** - User Management
**Purpose:** User registration and profile management (minimal, uses Django User)

---

### 10. **apps/vitals/** - Vital Signs Tracking
**Purpose:** Track patient vital signs (blood pressure, temperature, etc.)
**Status:** Planned, not yet implemented

---

## 🔐 AUTHENTICATION FLOW

### JWT Token-Based Authentication
```
1. Patient Registration:
   POST /api/v1/patients/register/
   → Creates User + Patient
   → Returns JWT tokens (access + refresh)

2. Patient Login:
   POST /api/v1/patients/login/
   → Authenticates by username or national_id
   → Returns JWT tokens

3. Token Refresh:
   POST /api/token/refresh/
   → Exchanges refresh token for new access token

4. Authenticated Requests:
   GET /api/v1/patients/me/
   Header: Authorization: Bearer <access_token>
   → Returns current patient data
```

### Permission Hierarchy
```
Admin (is_staff=True)
  ├─ Full access to all data
  └─ Can create/update/delete any resource

Nurse (has NurseProfile)
  ├─ View assigned patients
  ├─ Manage alerts
  └─ Update patient status

Patient (has Patient profile)
  ├─ View own data only
  ├─ Update own profile
  ├─ Request appointments
  └─ Report symptoms

Unauthenticated
  ├─ Register (POST /patients/register/)
  └─ Login (POST /patients/login/)
```

---

## 📊 DATA FLOW EXAMPLES

### Example 1: Patient Discharge → Home Care
```
1. Hospital discharges patient
   → Staff creates DischargeSummary (risk_level='high')
   → Prescriptions created (3 medications, 2x daily)

2. Alert Engine runs (every 10 min)
   → Detects high-risk discharge
   → Creates PatientAlert (severity='high', sla_deadline=30 min)
   → Auto-assigns to available nurse

3. Adherence records created
   → For each medication, create MedicationAdherence records
   → scheduled_date=today, scheduled_time=[8:00, 20:00]

4. Celery task runs (every 5 min)
   → Finds adherence records where scheduled_time - 1 hour = now
   → Sends SMS reminder via Africa's Talking
   → Updates reminder_sent=True

5. Patient misses dose
   → scheduled_time passes, status still 'scheduled'
   → Alert Engine detects is_overdue=True
   → Creates PatientAlert (type='missed_medication')
   → Nurse receives alert in dashboard

6. Nurse contacts patient
   → Updates alert status to 'in_progress'
   → Logs action in AlertLog
   → Patient confirms took medication late
   → Nurse marks adherence as 'late', taken_at=now
   → Resolves alert
```

### Example 2: Appointment Reminder Flow
```
1. Discharge summary requires follow-up
   → Staff creates Appointment (7 days from discharge)
   → appointment_datetime = 2025-02-15 10:00

2. System creates reminders
   → AppointmentReminder (24 hours before)
   → AppointmentReminder (1 hour before)

3. Celery task runs hourly
   → Finds reminders where reminder_datetime <= now and status='pending'
   → Renders template: "Muraho {patient_name}, you have appointment at {hospital} on {date}"
   → Sends SMS via MessageService
   → Updates reminder status='sent'

4. Patient misses appointment
   → appointment_datetime passes, status='scheduled'
   → Alert Engine detects is_overdue=True
   → Creates PatientAlert (type='missed_appointment')
   → Nurse calls patient to reschedule
```

---

## 🧪 TESTING STRATEGY

### Test Coverage: 81.44% (511 tests passing)

**Test Structure:**
```
apps/{module}/tests/
  ├── factories.py       # Factory Boy factories for test data
  ├── test_models.py     # Model logic, properties, validations
  ├── test_serializers.py # Serialization, validation
  ├── test_views.py      # ViewSet actions, permissions
  ├── test_api.py        # API integration tests
  └── test_services.py   # Service layer (messaging, alerts)
```

**Testing Philosophy:**
- TDD (Test-Driven Development): Write tests before implementation
- Factory Boy: Generate realistic test data
- pytest fixtures: Reusable test setup
- Mocking: Mock external APIs (Africa's Talking)
- Coverage target: >95% for production code

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Development Environment
```
Docker Compose:
  ├── postgres:15      # Database
  ├── redis:7          # Cache + Celery broker
  ├── django           # Web server (runserver)
  ├── celery-worker    # Background tasks
  └── celery-beat      # Periodic task scheduler
```

### Production (Planned)
```
AWS/Azure:
  ├── RDS PostgreSQL   # Managed database
  ├── ElastiCache Redis # Managed cache
  ├── ECS/EKS          # Container orchestration
  ├── S3               # Static files
  ├── CloudFront       # CDN
  └── Route53          # DNS
```

---

## 🔄 CELERY TASKS (Async Processing)

### Periodic Tasks (celery-beat)
```python
# Every 5 minutes
process_message_queue()
  → Send pending messages

# Every 10 minutes
run_alert_engine()
  → Check for patient issues
  → Create alerts
  → Assign to nurses

# Every hour
send_appointment_reminders()
  → Find due reminders
  → Send SMS/WhatsApp

# Daily at midnight
generate_adherence_records()
  → Create next day's adherence records
  → Based on active prescriptions
```

### On-Demand Tasks
```python
send_sms_async(phone, message)
  → Async SMS sending

send_email_async(to, subject, body)
  → Async email sending
```

---

## 📱 RWANDA-SPECIFIC FEATURES

### National ID Validation
```python
Regex: ^\d{16}$
Example: 1234567890123456
Unique constraint enforced
```

### Phone Number Format
```python
Regex: ^\+250\d{9}$
Example: +250788123456
Rwanda country code: +250
```

### Administrative Structure
```
Province (Intara) → 5 provinces
  ├── District (Akarere) → 30 districts
      ├── Sector (Umurenge) → 416 sectors
          ├── Cell (Akagari) → 2,148 cells
              └── Village (Umudugudu) → 14,837 villages
```

### Language Support
```
Primary: Kinyarwanda (kin)
Official: English (eng), French (fra)
Bilingual fields: instructions, warnings, notes
```

---

## 🎯 KEY DESIGN PATTERNS

### 1. Service Layer Pattern
```python
# Don't put business logic in views
# Use service classes

class MessageService:
    def send_message(patient, content, message_type):
        # Business logic here
        pass

# View just calls service
def send_reminder(request):
    MessageService.send_message(...)
```

### 2. Factory Pattern (Test Data)
```python
class PatientFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    national_id = factory.Sequence(lambda n: f'{n:016d}')
    # Generates realistic test data
```

### 3. Computed Properties
```python
class Prescription:
    @property
    def is_current(self):
        # Computed on-the-fly, not stored
        return self.is_active and self.start_date <= today <= self.end_date
```

### 4. Signal Handlers (Future)
```python
@receiver(post_save, sender=DischargeSummary)
def create_adherence_records(sender, instance, created, **kwargs):
    if created:
        # Auto-create adherence records for prescriptions
        pass
```

---

## 🔮 FUTURE PHASES (Weeks 4-32)

### Phase 2: SMS/WhatsApp (Weeks 5-8)
- Africa's Talking production credentials
- Two-way messaging (patient replies)
- Kinyarwanda NLP

### Phase 3: AI Chatbot (Weeks 9-12)
- PGVector embeddings
- RAG (Retrieval-Augmented Generation)
- Symptom checker with red flags
- Auto-escalation to nurses

### Phase 4: Care Guides (Weeks 13-16)
- Abafasha mobile app
- Home visit scheduling
- GPS navigation to patient homes
- Patient feedback collection

### Phase 5: Dashboards (Weeks 17-20)
- Hospital provider dashboards
- Insurance/RSSB integration
- Cost savings analytics

### Phase 6: Production (Weeks 21-32)
- USSD for feature phones
- React Native patient app
- Full production deployment
- Nationwide rollout

---

## 📈 SUCCESS METRICS

### Technical Metrics
- Test coverage: >95%
- API response time: <200ms (p95)
- SMS delivery rate: >98%
- Alert response time: <10 min (critical)

### Healthcare Metrics
- Medication adherence: >80%
- Appointment attendance: >85%
- Readmission reduction: 30%
- Patient satisfaction: >4.5/5

---

## 🎓 LEARNING RESOURCES

### For New Developers
1. Read this document first
2. Review models.py in each app (data structure)
3. Review views.py (API endpoints)
4. Run tests: `pytest apps/patients/tests/ -v`
5. Check API docs: http://localhost:8000/api/docs/

### Key Files to Understand
```
backend/apps/patients/models.py       # Core patient data
backend/apps/enrollment/models.py     # Discharge summaries
backend/apps/medications/models.py    # Prescriptions & adherence
backend/apps/nursing/alert_engine.py  # Alert logic
backend/apps/messaging/services.py    # SMS sending
backend/bicare360/settings/base.py    # Configuration
```

---

**End of Deep Index**
