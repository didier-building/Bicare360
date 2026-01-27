# BiCare360 Patient Portal - Complete Feature Specification
## With Global Health Data Systems Standards Compliance (FHIR, HL7, ICD-10, SNOMED CT)

## PHASE 1 MVP: Patient Authentication & Core Features

### ✅ TIER 1: Authentication (DONE)
- [x] Patient registration with bio data
- [x] Patient login (username OR national_id)
- [x] JWT token-based sessions
- [x] Password management

### 🔄 TIER 2: Patient Dashboard (IN PROGRESS)
**Main entry point after authentication**
- [ ] Patient profile display (name, contact, DOB, gender, blood type)
- [ ] Quick stats cards:
  - Active medications count
  - Upcoming appointments count
  - Recent discharge summaries count
  - Pending alerts count
- [ ] Last updated timestamps
- [ ] Edit profile button
- [ ] Logout button

---

## COMPLIANCE WITH GLOBAL HEALTH DATA STANDARDS

### Standards to Support:
1. **FHIR (Fast Healthcare Interoperability Resources)**
   - Patient resource representation
   - Medication resource representation
   - Appointment resource representation
   - Observation resource (vital signs, lab results)
   - Export patient data as FHIR JSON/XML

2. **HL7 v2.5 / v3**
   - Message structure for data exchange
   - Integration with legacy systems
   - ADT (Admission, Discharge, Transfer) messages

3. **Medical Coding Standards**
   - **ICD-10** - Diagnosis coding (e.g., E11.9 for Type 2 Diabetes)
   - **ICD-10-PCS** - Procedure coding
   - **SNOMED CT** - Clinical terminology (comprehensive clinical concepts)
   - **LOINC** - Laboratory observation codes
   - **RxNorm** - Medication coding

4. **Data Security & Privacy**
   - **HL7 Security Label Service (SLS)** - Data classification
   - **HIPAA** compliance (US standard)
   - **GDPR** compliance (EU standard)
   - **OpenID Connect** for authentication
   - **OAuth 2.0** for authorization

5. **Data Exchange Formats**
   - **XML** - Legacy systems
   - **JSON** - Modern systems (preferred)
   - **HL7 CDA** (Clinical Document Architecture) - Structured documents
   - **PDF/A** - Discharge summaries archival

---

## PATIENT SELF-SERVICE FEATURES (Updated with Health Standards)

## PATIENT SELF-SERVICE FEATURES (Updated with Health Standards)

### 🔴 HIGH PRIORITY - Phase 1 MVP (Week 1-2)

#### A. APPOINTMENT BOOKING & REQUEST SYSTEM
**Patient-Initiated Appointments**
- [ ] Request appointment with healthcare provider
  - Select appointment type (SNOMED CT codes for appointment types)
  - Select preferred date/time range
  - Select location (hospital/home visit/telemedicine)
  - Add chief complaint (ICD-10 code + description)
  - Add symptoms/reason for visit
  - Attach documents if needed
  - Priority level selection

- [ ] Track appointment requests
  - Status tracking (pending/confirmed/cancelled/completed)
  - Confirmation notification
  - Appointment reminder (24hrs, 2hrs before)
  - Provider notes visible to patient
  - Post-appointment follow-up instructions

- [ ] Data Format
  - Store using FHIR Appointment resource
  - Export as FHIR JSON/XML
  - Patient can download appointment details

#### B. CAREGIVER BOOKING SYSTEM (Marketplace)
**Book Home Care/Support Services**
- [ ] Browse caregivers
  - Filter by service type (nursing care, physical therapy, eldercare, etc.)
  - Filter by availability
  - View caregiver profiles (experience, qualifications, ratings)
  - View pricing
  - View patient reviews

- [ ] Book caregiver services
  - Select caregiver
  - Select service type (SNOMED CT codes for care services)
  - Select date/time
  - Set duration (hours)
  - Specify care needs
  - Payment method
  - Special instructions

- [ ] Manage caregiver bookings
  - View confirmed bookings
  - Reschedule/cancel bookings
  - Communicate with caregiver
  - Rate and review after service
  - Payment history

- [ ] Data Format
  - Store service requests with standardized codes
  - Track care activities
  - Generate care summaries

---

### 🟠 MEDIUM PRIORITY - Phase 1 Core (Week 2-3)

#### 1️⃣ MEDICATIONS MANAGEMENT (FHIR Compliant)
**Display & Track Medications**
- [ ] Current active medications list
  - Medication name (RxNorm code + generic + brand)
  - Dosage (FHIR format)
  - Frequency (e.g., twice daily - FHIR Timing)
  - Route (oral, injection, topical - SNOMED CT codes)
  - Start date & end date
  - Days remaining
  - Prescriber name
  - Indication (ICD-10 code + description)
  - Contraindications
  - Side effects warning

- [ ] Medication adherence tracking
  - View scheduled doses (calendar view)
  - Mark dose as "taken" with timestamp
  - Mark dose as "missed" with reason
  - View adherence history
  - Adherence percentage per medication
  - Weekly/monthly adherence charts
  - Visual indicators (on track, at risk, non-compliant)
  - Report side effects

- [ ] Prescription management
  - View full prescription details (FHIR format)
  - Download prescription as PDF/FHIR
  - Request refills
  - View refill history
  - Medication interactions check

- [ ] Data Format
  - FHIR Medication resource
  - FHIR MedicationStatement resource
  - FHIR MedicationAdherence resource
  - RxNorm coding for all medications

#### 2️⃣ HEALTH RECORDS & DISCHARGE SUMMARIES (HL7 CDA Compliant)
**View & Manage Medical Records**
- [ ] Discharge summaries list
  - Hospital name
  - Admission date / Discharge date
  - Diagnosis (ICD-10 codes)
  - Primary procedures (ICD-10-PCS codes)
  - Attending physician
  - Medications at discharge
  - Status (active/archived)
  - Download as PDF/FHIR/HL7 CDA

- [ ] Detailed discharge information
  - Chief complaint
  - History of present illness
  - Physical examination findings
  - Assessment & Plan
  - Medications at discharge (with RxNorm codes)
  - Follow-up instructions
  - Precautions & restrictions
  - Dietary restrictions
  - Activity restrictions
  - Return precautions
  - Test results & lab values (LOINC codes)

- [ ] Lab results & diagnostic reports
  - Lab test names (LOINC codes)
  - Results with units & reference ranges
  - Date performed
  - Performing lab
  - Abnormal values highlighted

- [ ] Data Format
  - FHIR Document Bundle (CDA equivalent)
  - HL7 CDA R2 format
  - FHIR Observation resources (for labs)
  - ICD-10 & ICD-10-PCS coding
  - LOINC codes for lab tests

#### 3️⃣ APPOINTMENTS MANAGEMENT (FHIR Compliant)
**Schedule & Manage Appointments**
- [ ] View all appointments
  - Date, time, location (SNOMED CT codes)
  - Appointment type (SNOMED CT codes)
  - Healthcare provider name & specialty
  - Department
  - Status (scheduled, confirmed, completed, cancelled, no-show)
  - Notes/reason for appointment
  - Pre-appointment instructions

- [ ] Appointment calendar view
  - Monthly/weekly calendar
  - Filter by provider/type/status
  - Color coding by status
  - Appointment reminders
  - Integration with personal calendar (iCal export)

- [ ] Post-appointment
  - View provider notes
  - Download visit summary
  - Access prescribed medications
  - Schedule follow-up
  - Access test requisitions

- [ ] Data Format
  - FHIR Appointment resource
  - FHIR Encounter resource (for completed visits)
  - Calendar export (iCalendar format)

---

### 🟡 LOWER PRIORITY - Phase 1 Extended (Week 3-4)

#### 4️⃣ HEALTH ALERTS & NOTIFICATIONS
**Receive Important Health Alerts**
- [ ] Alert dashboard
  - List of active alerts with severity
  - Timestamp & source
  - Mark as read/dismiss
  - Alert history

- [ ] Alert types (with SNOMED CT codes)
  - Missed medication alerts
  - Missed appointment alerts
  - High-risk discharge alerts
  - Medication side effect alerts
  - Readmission risk alerts
  - Lab abnormality alerts
  - Appointment reminders

- [ ] Alert delivery
  - In-app notifications
  - Email notifications
  - SMS notifications
  - Notification preferences per type

#### 5️⃣ PATIENT PROFILE & SETTINGS (FHIR Compliant)
**Manage Personal Information**
- [ ] Edit profile
  - First name, last name
  - Email, phone number
  - Date of birth
  - Gender (standard codes)
  - Blood type (standard codes)
  - Emergency contacts
  - Preferred language
  - Accessibility needs

- [ ] Communication preferences
  - Preferred language
  - SMS preference (opt-in/out)
  - Email preference (opt-in/out)
  - Preferred contact method & time

- [ ] Account management
  - Change password
  - View login history
  - Session management
  - Two-factor authentication (optional Phase 2)

- [ ] Data Format
  - FHIR Patient resource
  - FHIR ContactPoint resources
  - Standard coding for gender, blood type

#### 6️⃣ CONSENT & PRIVACY (GDPR + HIPAA Compliant)
**GDPR & HIPAA Compliance**
- [ ] Consent management
  - View all signed consents
  - Consent date & type
  - Withdraw consent
  - Re-consent for new purposes

- [ ] Consent types
  - Treatment consent
  - Data access consent
  - Emergency access consent
  - Research participation consent
  - Caregiver access consent

- [ ] Data rights (GDPR Article 15-21)
  - Request data access (Article 15)
  - Request data export (Article 20 - FHIR format)
  - Request data deletion (Article 17 - "right to be forgotten")
  - Request data rectification (Article 16)
  - View data access logs (audit trail)

- [ ] Data Format
  - FHIR Consent resource
  - Exportable as FHIR XML/JSON
  - Audit log of all data access

#### 7️⃣ EMERGENCY CONTACTS & CAREGIVER PERMISSIONS
**Manage Access & Authorizations**
- [ ] Emergency contacts
  - Contact name, relationship, phone
  - Emergency access permissions
  - Can contact in case of emergency

- [ ] Caregiver permissions
  - Grant/revoke access to specific caregivers
  - Set permission level (view only, make appointments, etc.)
  - Time-limited access
  - Audit log of caregiver access

---

### 🟢 OPTIONAL/PHASE 2 FEATURES

#### 8️⃣ HEALTH METRICS & MONITORING (FHIR Compliant)
**Track Vital Signs & Health Metrics**
- [ ] Vital signs tracking
  - Blood pressure (LOINC code: 85354-9)
  - Heart rate (LOINC code: 8867-4)
  - Weight (LOINC code: 29463-7)
  - Temperature (LOINC code: 8310-5)
  - Blood glucose (LOINC code: 2345-7)
  - Oxygen saturation (LOINC code: 59408-5)

- [ ] Health trends
  - Chart visualization of vitals
  - Alerts for abnormal readings
  - Goal tracking (e.g., target weight)
  - Integration with wearable devices (optional)

- [ ] Data Format
  - FHIR Observation resource
  - LOINC codes for all measurements
  - Standard units (SI units)

#### 9️⃣ HEALTH INFORMATION EXCHANGE (HIE)
**Share Data with Other Providers**
- [ ] Data sharing
  - Share records with new providers
  - Grant temporary access
  - Track who accessed data
  - Revoke access anytime

- [ ] Patient-initiated data requests
  - Request transfer of records to new provider
  - Automatic transmission in standard format
  - Confirmation of receipt

- [ ] Data Format
  - FHIR format for exchange
  - HL7 CDA for document exchange
  - Encrypted transmission

#### 🔟 MEDICATION INFORMATION LIBRARY
**Learn About Medications**
- [ ] View detailed medication information
  - Indications
  - Contraindications
  - Side effects & frequency
  - Drug interactions
  - Precautions
  - Storage instructions
  - Cost/insurance information
  - Alternative medications

- [ ] Interaction checker
  - Check interactions with current medications
  - Check with supplements/OTC drugs
  - Safety warnings

---

## CORE DATA STANDARDS IMPLEMENTATION ROADMAP

## CORE DATA STANDARDS IMPLEMENTATION ROADMAP

### Phase 1: Foundation Standards (Week 1-2)
- ✅ Basic FHIR Patient resource
- ✅ FHIR Medication & MedicationStatement
- ✅ FHIR Appointment resources
- ✅ ICD-10 diagnosis coding
- ✅ RxNorm medication coding
- ✅ SNOMED CT for care types

### Phase 2: Interoperability (Week 3-4)
- FHIR Document Bundle export
- HL7 CDA generation
- FHIR Observation resources (labs)
- LOINC coding for lab results
- XML/JSON export capabilities

### Phase 3: Advanced (Phase 2+)
- Full HL7 v2.5 messaging
- Health Information Exchange (HIE)
- DICOM support (if imaging needed)
- CPT/HCPCS procedure coding
- Advanced consent management (FHIR Consent)

---

## RECOMMENDED IMPLEMENTATION PRIORITY

### 🚀 PHASE 1 (Week 1-2) - MVP Foundation
**Priority Order:**
1. ✅ Patient Authentication (DONE)
2. Patient Dashboard (in progress)
3. **Appointment Booking System** ⭐ HIGH PRIORITY
4. **Caregiver Booking System** ⭐ HIGH PRIORITY
5. Medications Management (with adherence)
6. Health Alerts & Notifications

### 📊 PHASE 2 (Week 3-4) - Full Patient Portal
7. Discharge Summaries & Medical Records
8. Patient Profile & Settings
9. Consent & Privacy Management
10. Health Metrics & Monitoring
11. Data Export (FHIR/HL7 formats)

### 🎯 PHASE 3 (Phase 2+ Future)
12. Health Information Exchange (HIE)
13. Secure Messaging with Providers
14. Advanced Analytics & Insights
15. Mobile App & Wearable Integration

---

## TECHNICAL ARCHITECTURE NOTES

### Backend Needs:
- FHIR R4 JSON serializers for all patient data
- Standard code systems (ICD-10, RxNorm, SNOMED CT, LOINC)
- Appointment booking workflow
- Caregiver/marketplace integration
- Data export endpoints (FHIR, HL7 CDA, PDF)
- Audit logging for HIPAA/GDPR compliance

### Frontend Needs:
- Appointment booking UI (calendar, form)
- Caregiver browsing & booking UI
- Medication adherence tracker
- Health alerts dashboard
- Data export functionality
- Responsive mobile design

---

## SUMMARY

**Total Core Features for Phase 1 MVP:**
- ✅ 2 Done (Authentication)
- 🔴 2 High Priority (Appointments, Caregiver Booking)
- 🟠 3 Core (Medications, Health Records, Alerts)
- 🟡 2 Extended (Profile, Consent)
- 🟢 3 Optional (Health Metrics, HIE, Library)

**Health Standards Compliance:**
- ✅ FHIR R4 data models
- ✅ ICD-10/ICD-10-PCS diagnosis & procedure codes
- ✅ RxNorm medication codes
- ✅ SNOMED CT for clinical concepts
- ✅ LOINC for lab codes
- ✅ GDPR/HIPAA compliance framework
- ✅ Data export in standard formats

**Estimated Timeline:** 4-6 weeks for Phase 1+2

---

**Ready to implement? Which should I start with?**
1. **Appointment Booking System** (high impact, enables patient self-service)
2. **Caregiver Booking/Marketplace** (revenue-generating feature)
3. **Medications Management** (core health tracking)
4. **All of the above** (full Phase 1)
