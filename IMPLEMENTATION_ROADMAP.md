# BiCare360 Implementation Roadmap
## Hybrid Care Bridge - Complete Build Plan

**Vision:** AI + Human care coordination platform ensuring no patient feels lost after hospital discharge

**Timeline:** 6 Months (26 weeks)  
**Approach:** TDD with 95%+ coverage  
**Deployment:** Progressive rollouts with hospital pilots

---

## 🎯 Strategic Priorities

### P0 - Critical (MVP for Hospital Pilot)
Must have for initial launch with pilot hospital
- Complete enrollment with discharge data
- SMS medication reminders
- Nurse triage with red flag alerts
- Basic hospital dashboard

### P1 - High Priority (3-Month Mark)
Essential for scaling beyond pilot
- WhatsApp integration
- AI chatbot (Kinyarwanda)
- Care guide booking system
- Insurance dashboard

### P2 - Nice to Have (6-Month Mark)
Enhance user experience
- USSD for feature phones
- Mobile apps (native)
- Advanced analytics
- Multi-hospital support

---

## Phase 1: Complete Enrollment System (Weeks 1-4) ✅ 40% DONE

### Week 1: Discharge Summary & Hospital Integration

**Models:**
```python
# apps/enrollment/models.py
class Hospital:
    - name, code, location, contact
    - emr_integration_type (manual, API, HL7)
    - status (active, pilot, inactive)
    
class DischargeSummary:
    - patient (FK)
    - hospital (FK)
    - admission_date, discharge_date
    - diagnosis (TextField) - primary & secondary
    - treatment_summary (TextField)
    - discharge_instructions (TextField)
    - discharge_medications (M2M)
    - follow_up_required (Boolean)
    - risk_level (low, medium, high)
    - created_by (nurse/CHW)
```

**API Endpoints:**
- `POST /api/v1/discharge/` - Create discharge summary
- `GET /api/v1/discharge/{id}/` - Retrieve discharge details
- `PATCH /api/v1/discharge/{id}/` - Update summary
- `GET /api/v1/hospitals/` - List hospitals

**Tests:** 30+ tests (unit, integration, edge cases)

### Week 2: Medication Management System

**Models:**
```python
class MedicationCatalog:
    - generic_name, brand_names
    - dosage_forms (tablet, syrup, injection)
    - standard_dosages
    - contraindications
    - side_effects
    
class Prescription:
    - patient (FK)
    - discharge_summary (FK, optional)
    - prescribed_by (doctor name)
    - prescribed_date
    - status (active, completed, cancelled)
    
class PrescribedMedication:
    - prescription (FK)
    - medication (FK to catalog)
    - dosage (e.g., "50mg")
    - frequency (e.g., "twice daily", "every 8 hours")
    - route (oral, topical, injection)
    - duration_days
    - start_date, end_date
    - refills_remaining
    - special_instructions (Kinyarwanda + English)
    
class MedicationAdherence:
    - prescribed_medication (FK)
    - scheduled_time
    - taken_time (nullable)
    - status (taken, missed, skipped, late)
    - confirmed_by (patient, family, system)
    - notes
```

**API Endpoints:**
- `POST /api/v1/prescriptions/` - Create prescription
- `GET /api/v1/prescriptions/?patient={id}&status=active` - List active prescriptions
- `POST /api/v1/prescriptions/{id}/medications/` - Add medication
- `PATCH /api/v1/medications/{id}/` - Update medication
- `POST /api/v1/adherence/log/` - Log medication taken/missed
- `GET /api/v1/adherence/report/?patient={id}` - Adherence report

**Business Logic:**
- Auto-calculate end dates from start_date + duration
- Alert when refills needed (3 days before)
- Track adherence percentage
- Flag concerning patterns (3+ consecutive misses)

**Tests:** 40+ tests

### Week 3: Appointment & Follow-up System

**Models:**
```python
class AppointmentType:
    - name (Follow-up, Specialist, Lab, Imaging)
    - description
    - estimated_duration
    
class Appointment:
    - patient (FK)
    - appointment_type (FK)
    - hospital/clinic (FK)
    - provider_name
    - scheduled_date, scheduled_time
    - status (scheduled, confirmed, completed, missed, cancelled)
    - reason (TextField)
    - related_discharge (FK, optional)
    - reminder_sent_count
    - last_reminder_sent
    
class AppointmentReminder:
    - appointment (FK)
    - reminder_type (SMS, WhatsApp, call)
    - scheduled_send_time
    - sent_time (nullable)
    - status (pending, sent, failed, delivered, read)
    - message_content
```

**API Endpoints:**
- `POST /api/v1/appointments/` - Schedule appointment
- `GET /api/v1/appointments/?patient={id}&status=scheduled` - Upcoming appointments
- `PATCH /api/v1/appointments/{id}/confirm/` - Patient confirms
- `PATCH /api/v1/appointments/{id}/reschedule/` - Reschedule
- `POST /api/v1/appointments/{id}/mark-missed/` - Mark missed
- `GET /api/v1/appointments/missed/` - List missed appointments

**Celery Tasks:**
- Send reminder 24 hours before
- Send reminder 2 hours before
- Mark as missed if no-show
- Follow-up for missed appointments

**Tests:** 35+ tests

### Week 4: Consent & Privacy Management

**Models:**
```python
class ConsentType:
    - name (Monitoring, Data Sharing, SMS Communication, Research)
    - description_kinyarwanda, description_english, description_french
    - is_required (Boolean)
    
class PatientConsent:
    - patient (FK)
    - consent_type (FK)
    - granted (Boolean)
    - granted_date
    - granted_by (patient, family_member)
    - witness (CHW/Nurse name)
    - expires_date (nullable)
    - withdrawn_date (nullable)
    - digital_signature (optional)
    
class DataAccessLog:
    - patient (FK)
    - accessed_by (user)
    - access_type (view, edit, export)
    - data_category (demographics, medical, financial)
    - timestamp
    - ip_address
    - reason (TextField)
```

**API Endpoints:**
- `POST /api/v1/consent/` - Record consent
- `GET /api/v1/consent/?patient={id}` - View consents
- `PATCH /api/v1/consent/{id}/withdraw/` - Withdraw consent
- `GET /api/v1/audit/access-log/?patient={id}` - Privacy audit trail

**GDPR Compliance:**
- Right to access (export patient data)
- Right to be forgotten (anonymize, not delete)
- Right to rectification
- Consent management
- Audit logging (7-year retention)

**Tests:** 25+ tests

**Week 4 Total:** 130+ comprehensive tests for complete enrollment

---

## Phase 2: Messaging & Reminders (Weeks 5-8)

### Week 5: SMS Integration - Africa's Talking

**Setup:**
```bash
pip install africastalking
```

**Models:**
```python
class SMSProvider:
    - name (Africa's Talking, Twilio)
    - api_key_encrypted
    - sender_id
    - is_active
    - cost_per_sms
    
class SMSMessage:
    - patient (FK)
    - phone_number
    - message_text_kinyarwanda
    - message_text_english
    - language_sent (kin, eng, fra)
    - message_type (medication_reminder, appointment_reminder, health_tip, alert)
    - related_object (Generic FK: Medication, Appointment, etc.)
    - scheduled_send_time
    - sent_time (nullable)
    - delivery_status (pending, sent, delivered, failed, bounced)
    - delivery_time
    - cost
    - error_message
    
class SMSTemplate:
    - name
    - message_type
    - template_kinyarwanda
    - template_english
    - template_french
    - variables (JSON: {patient_name}, {medication_name}, etc.)
```

**API Integration:**
```python
# services/sms_service.py
class SMSService:
    def send_medication_reminder(prescribed_medication):
        """Send reminder: 'Aimé, it's time for your blood pressure pill.'"""
        
    def send_appointment_reminder(appointment):
        """Send reminder: 'You have a doctor appointment tomorrow at 9 AM.'"""
        
    def send_health_tip(patient, tip):
        """Send daily health tip in patient's language"""
        
    def send_alert_to_nurse(alert):
        """Send urgent alert to on-call nurse"""
```

**Celery Tasks:**
```python
@shared_task
def process_medication_reminders():
    """Run every 30 minutes - check due medications, send reminders"""
    
@shared_task
def process_appointment_reminders():
    """Run every hour - check upcoming appointments"""
    
@shared_task
def send_daily_health_tips():
    """Run daily at 8 AM - send health tips"""
    
@shared_task
def retry_failed_sms():
    """Run every 15 minutes - retry failed SMS"""
```

**Tests:** 45+ tests (SMS sending, templating, delivery tracking, error handling)

### Week 6: WhatsApp Business API Integration

**Setup:**
- Apply for WhatsApp Business API (Meta)
- Get approved phone number (+250...)
- Set up webhook for incoming messages

**Models:**
```python
class WhatsAppConversation:
    - patient (FK)
    - whatsapp_phone
    - status (active, ended)
    - started_at, ended_at
    - last_message_at
    
class WhatsAppMessage:
    - conversation (FK)
    - direction (inbound, outbound)
    - message_type (text, image, document, location, audio)
    - content (TextField for text, URL for media)
    - template_name (for outbound template messages)
    - sent_time
    - delivered_time
    - read_time
    - status (sent, delivered, read, failed)
```

**API Endpoints:**
- `POST /api/v1/whatsapp/send/` - Send WhatsApp message
- `POST /webhook/whatsapp/` - Receive incoming messages
- `GET /api/v1/whatsapp/conversations/{patient_id}/` - Get conversation history

**Features:**
- Rich medication reminders with images
- Share discharge instructions (PDF)
- Interactive buttons (Yes/No for "Did you take your meds?")
- Location sharing for home visits

**Tests:** 40+ tests

### Week 7: Kinyarwanda Message Templates & Localization

**Message Library:**
```python
# services/message_templates.py
MEDICATION_REMINDERS = {
    'kin': "Mwaramutse {name}, ni igihe cyo gufata umuti wawe: {medication}",
    'eng': "Good morning {name}, it's time for your medication: {medication}",
    'fra': "Bonjour {name}, il est temps de prendre votre médicament: {medication}"
}

APPOINTMENT_REMINDERS = {
    'kin': "Ejo {name} ufite gahunda yo kwa muganga saa {time}",
    'eng': "Tomorrow {name} you have a doctor's appointment at {time}",
    'fra': "Demain {name} vous avez rendez-vous chez le médecin à {time}"
}

ADHERENCE_CHECK = {
    'kin': "Wafashe umuti wawe? Subiza: 1=Yego, 2=Oya",
    'eng': "Did you take your medication? Reply: 1=Yes, 2=No",
    'fra': "Avez-vous pris votre médicament? Répondre: 1=Oui, 2=Non"
}
```

**Two-way SMS Handling:**
```python
@api_view(['POST'])
def handle_incoming_sms(request):
    """
    Handle patient responses:
    - "1" or "Yego" -> Log medication taken
    - "2" or "Oya" -> Log missed, alert nurse if pattern
    - Free text -> Parse intent, respond or escalate
    """
```

**Tests:** 30+ tests (template rendering, language selection, SMS parsing)

### Week 8: Adherence Tracking & Reporting

**Analytics:**
```python
class AdherenceReport:
    - patient (FK)
    - report_period (week, month)
    - start_date, end_date
    - total_scheduled_doses
    - doses_taken
    - doses_missed
    - adherence_rate (percentage)
    - longest_streak
    - concerning_patterns (JSON)
    - generated_at
```

**API Endpoints:**
- `GET /api/v1/adherence/report/{patient_id}/?period=week` - Get adherence report
- `GET /api/v1/adherence/alerts/` - List concerning adherence patterns
- `GET /api/v1/adherence/leaderboard/?hospital={id}` - Best adherence patients

**Celery Tasks:**
```python
@shared_task
def generate_weekly_adherence_reports():
    """Generate reports for all active patients every Monday"""
    
@shared_task
def detect_adherence_concerns():
    """Flag patients with <70% adherence or 3+ consecutive misses"""
```

**Tests:** 35+ tests

**Phase 2 Total:** 150+ tests for complete messaging system

---

## Phase 3: AI Chatbot & Symptom Checker (Weeks 9-12)

### Week 9: AI Service Architecture & RAG Setup

**Infrastructure:**
```bash
# New dependencies
pip install openai anthropic langchain pgvector psycopg2-binary
```

**Database:**
```sql
-- Enable PGVector extension
CREATE EXTENSION vector;

-- Embedding storage
CREATE TABLE medical_documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    document_type VARCHAR(50), -- protocol, guideline, faq
    source VARCHAR(200),
    language VARCHAR(10),
    created_at TIMESTAMP
);

-- Vector similarity index
CREATE INDEX ON medical_documents USING ivfflat (embedding vector_cosine_ops);
```

**Models:**
```python
class MedicalDocument:
    - title
    - content (TextField)
    - document_type (protocol, guideline, faq, drug_info)
    - source (Rwanda MoH, WHO, hospital policy)
    - language (kin, eng, fra)
    - embedding (vector field)
    - verified_by (medical professional)
    - last_updated
    
class ChatSession:
    - patient (FK, nullable for anonymous)
    - started_at, ended_at
    - language (kin, eng, fra)
    - escalated_to_nurse (Boolean)
    - satisfaction_rating
    
class ChatMessage:
    - session (FK)
    - role (user, assistant, system)
    - content (TextField)
    - intent (symptom_check, medication_question, general_health)
    - sentiment (positive, neutral, negative, urgent)
    - requires_escalation (Boolean)
    - timestamp
```

**RAG Service:**
```python
# services/ai_service.py
class RAGService:
    def embed_document(content, language):
        """Generate embeddings for medical documents"""
        
    def semantic_search(query, language, top_k=5):
        """Find relevant documents using vector similarity"""
        
    def generate_response(user_message, context_docs, conversation_history):
        """Generate safe, grounded response using LLM + RAG"""
        
    def detect_red_flags(message):
        """Identify urgent symptoms requiring immediate attention"""
```

**Red Flag Keywords:**
```python
RED_FLAGS = {
    'kin': ['umutwe urababaje cyane', 'ubucuti mu gituza', 'ndaruhuka nabi'],
    'eng': ['severe chest pain', 'difficulty breathing', 'severe bleeding'],
    'fra': ['douleur thoracique sévère', 'difficulté à respirer']
}
```

**Tests:** 50+ tests (embedding, search, response generation, red flag detection)

### Week 10: Symptom Checker Logic

**Models:**
```python
class SymptomCategory:
    - name (Cardiovascular, Respiratory, Digestive, etc.)
    - icon, color
    
class Symptom:
    - name_kinyarwanda, name_english, name_french
    - category (FK)
    - severity_level (mild, moderate, severe, emergency)
    - common_causes (TextField)
    - red_flags (TextField)
    
class SymptomReport:
    - patient (FK, nullable)
    - chat_session (FK)
    - symptoms (M2M to Symptom)
    - severity_self_assessed (1-10)
    - duration (hours/days)
    - additional_notes (TextField)
    - ai_assessment (TextField)
    - recommended_action (rest, monitor, see_doctor, emergency)
    - escalated_to_nurse (Boolean)
    - nurse_reviewed_at
    - created_at
```

**Decision Tree:**
```python
class SymptomChecker:
    def assess(symptoms, patient_history):
        """
        1. Check for red flags -> Immediate escalation
        2. Assess severity based on combination
        3. Check patient history (chronic conditions)
        4. Provide recommendation
        5. Schedule follow-up check if needed
        """
        
    def calculate_risk_score(symptoms, patient):
        """Return 0-100 risk score"""
```

**API Endpoints:**
- `POST /api/v1/ai/chat/start/` - Start chat session
- `POST /api/v1/ai/chat/{session_id}/message/` - Send message
- `POST /api/v1/ai/symptom-check/` - Submit symptoms
- `GET /api/v1/ai/health-tips/{patient_id}/` - Get personalized tips

**Tests:** 60+ tests (symptom logic, risk scoring, decision trees)

### Week 11: Kinyarwanda NLP & Language Support

**Challenges:**
- Limited Kinyarwanda training data
- Translation quality
- Medical terminology in Kinyarwanda

**Solutions:**
```python
# services/translation_service.py
class KinyarwandaNLP:
    def translate_to_english(kinyarwanda_text):
        """Use Google Translate API + custom medical dictionary"""
        
    def translate_to_kinyarwanda(english_text):
        """Translate response back to Kinyarwanda"""
        
    def normalize_text(text):
        """Handle common misspellings, abbreviations"""
        
    def detect_intent(message, language):
        """Classify message intent"""
```

**Medical Dictionary:**
```python
MEDICAL_TERMS = {
    'umutwe urababaje': 'headache',
    'ubucuti': 'chest pain',
    'kuruhuka nabi': 'difficulty breathing',
    'umukara': 'fever',
    # ... 500+ medical terms
}
```

**Tests:** 40+ tests (translation, intent detection, term mapping)

### Week 12: Conversation Management & Escalation

**Escalation Rules:**
```python
class EscalationEngine:
    def should_escalate(message, session_history, patient):
        """
        Escalate if:
        - Red flag symptoms detected
        - Patient explicitly requests human
        - AI confidence < 60%
        - Sensitive topic (mental health, abuse)
        - Medication interaction concern
        """
        
    def route_to_nurse(alert, patient):
        """Create triage case and notify on-call nurse"""
```

**Conversation Flows:**
```python
CONVERSATION_FLOWS = {
    'medication_question': [
        "I can help with medication questions. Which medication?",
        "When do you take {medication}?",
        "Are you experiencing side effects?",
        # Provide answer or escalate
    ],
    'symptom_check': [
        "I'm here to help. What symptoms are you experiencing?",
        "How long have you had these symptoms?",
        "On a scale of 1-10, how severe?",
        # Assess and recommend
    ]
}
```

**Tests:** 45+ tests (escalation logic, conversation flows, routing)

**Phase 3 Total:** 195+ tests for AI system

---

## Phase 4: Nurse Triage System (Weeks 13-16)

### Week 13: Alert Engine & Red Flag Detection

**Models:**
```python
class AlertType:
    - name (Red Flag Symptom, Missed Appointments, Low Adherence, Care Guide Concern)
    - severity (low, medium, high, critical)
    - response_sla_minutes (10 for critical)
    - escalation_after_minutes
    
class Alert:
    - patient (FK)
    - alert_type (FK)
    - severity
    - title
    - description (TextField)
    - source (ai_chatbot, medication_tracker, appointment_system, care_guide)
    - related_object (Generic FK)
    - triggered_at
    - acknowledged_by (nurse FK)
    - acknowledged_at
    - resolved_at
    - resolution_notes (TextField)
    - escalated (Boolean)
    - escalated_to (supervisor FK)
    
class AlertRule:
    - name
    - condition (JSON: {adherence_rate < 70, missed_doses >= 3})
    - alert_type (FK)
    - is_active (Boolean)
    - check_frequency_minutes
```

**Alert Triggers:**
```python
@shared_task
def check_adherence_alerts():
    """Flag patients with <70% adherence"""
    
@shared_task
def check_missed_appointment_alerts():
    """Alert for missed follow-ups"""
    
@shared_task
def check_symptom_alerts():
    """Process red flag symptoms from AI chat"""
    
@shared_task
def check_sla_breaches():
    """Escalate alerts exceeding response time SLA"""
```

**Tests:** 55+ tests

### Week 14: Nurse Console Dashboard

**Frontend Requirements:**
- Real-time alert feed
- Patient quick view
- Response time tracking
- Case management

**API Endpoints:**
```python
# Nurse Console APIs
GET  /api/v1/nurse/alerts/?status=pending&severity=high
POST /api/v1/nurse/alerts/{id}/acknowledge/
POST /api/v1/nurse/alerts/{id}/resolve/
POST /api/v1/nurse/alerts/{id}/escalate/
GET  /api/v1/nurse/patients/?assigned_to_me=true
GET  /api/v1/nurse/patients/{id}/timeline/
POST /api/v1/nurse/patients/{id}/call-log/
GET  /api/v1/nurse/performance/?date_range=week
```

**WebSocket for Real-time Updates:**
```python
# consumers.py
class NurseAlertConsumer(AsyncWebsocketConsumer):
    async def alert_created(self, event):
        """Push new alert to connected nurse"""
        
    async def alert_updated(self, event):
        """Update alert status in real-time"""
```

**Models:**
```python
class NurseProfile:
    - user (FK)
    - license_number
    - specialization
    - phone_number
    - whatsapp_number
    - is_on_call (Boolean)
    - max_concurrent_cases
    - assigned_hospitals (M2M)
    
class NurseResponse:
    - alert (FK)
    - nurse (FK)
    - response_time_minutes
    - action_taken (called_patient, called_family, scheduled_visit, escalated)
    - outcome (resolved, ongoing, escalated)
    - notes (TextField)
    - follow_up_required (Boolean)
    - follow_up_date
```

**Tests:** 50+ tests (real-time updates, assignment logic, SLA tracking)

### Week 15: Triage Protocol Engine

**Protocol Structure:**
```python
class TriageProtocol:
    - name (Chest Pain Protocol, Diabetes Management, Hypertension Follow-up)
    - condition_category
    - protocol_steps (JSON ordered steps)
    - decision_tree (JSON)
    - approved_by (medical director)
    - version
    - effective_date
    
class ProtocolStep:
    - protocol (FK)
    - step_number
    - instruction (TextField in multiple languages)
    - questions_to_ask (JSON)
    - red_flags_to_check (JSON)
    - next_step_logic (JSON conditional)
```

**Decision Support:**
```python
class TriageDecisionSupport:
    def get_protocol(symptoms, patient_history):
        """Match symptoms to appropriate protocol"""
        
    def walk_through_protocol(protocol, patient_responses):
        """Guide nurse through protocol steps"""
        
    def suggest_next_action(current_step, responses):
        """AI-assisted next step recommendation"""
```

**Tests:** 45+ tests (protocol matching, decision trees)

### Week 16: Performance Analytics & Quality Assurance

**Metrics:**
```python
class NursePerformanceMetric:
    - nurse (FK)
    - date
    - total_alerts_handled
    - average_response_time_minutes
    - sla_compliance_rate
    - escalation_rate
    - patient_satisfaction_score
    - cases_resolved
    
class QualityReview:
    - nurse_response (FK)
    - reviewed_by (supervisor)
    - protocol_adherence_score (1-5)
    - communication_score (1-5)
    - outcome_appropriateness (1-5)
    - feedback (TextField)
    - requires_retraining (Boolean)
```

**API Endpoints:**
```python
GET /api/v1/supervisor/performance/?nurse={id}&period=month
GET /api/v1/supervisor/quality-reviews/?status=pending
POST /api/v1/supervisor/quality-reviews/
GET /api/v1/analytics/response-times/
GET /api/v1/analytics/alert-trends/
```

**Tests:** 40+ tests

**Phase 4 Total:** 190+ tests for triage system

---

## Phase 5: Abafasha Care Guide System (Weeks 17-20)

### Week 17: Care Guide Management

**Models:**
```python
class CareGuide:
    - user (FK)
    - first_name, last_name
    - phone_number, whatsapp
    - national_id
    - certification_level (basic, intermediate, advanced)
    - certification_date, certification_expiry
    - specializations (M2M: wound_care, vitals_monitoring, mobility_assistance)
    - service_areas (M2M to Sectors)
    - availability_schedule (JSON)
    - rating_average
    - total_visits
    - status (active, inactive, suspended)
    - background_check_status
    - profile_photo
    
class CareGuideDocument:
    - care_guide (FK)
    - document_type (certification, id_copy, insurance, training_record)
    - file_url
    - verified (Boolean)
    - verified_by
    - verified_date
```

**API Endpoints:**
```python
POST /api/v1/care-guides/
GET  /api/v1/care-guides/?available=true&sector={id}
GET  /api/v1/care-guides/{id}/
PATCH /api/v1/care-guides/{id}/availability/
GET  /api/v1/care-guides/{id}/reviews/
```

**Tests:** 40+ tests

### Week 18: Service Booking System

**Models:**
```python
class ServiceType:
    - name (Vitals Check, Wound Dressing, Medication Administration, Mobility Support)
    - description_kinyarwanda, description_english
    - estimated_duration_minutes
    - base_price (RWF)
    - requires_certification_level
    
class ServiceRequest:
    - patient (FK)
    - requested_by (family member name, phone)
    - service_types (M2M)
    - preferred_date, preferred_time
    - location (address FK or manual address)
    - special_instructions (TextField)
    - urgency (routine, same_day, urgent)
    - status (pending, assigned, confirmed, in_progress, completed, cancelled)
    - created_at
    
class ServiceBooking:
    - service_request (FK)
    - care_guide (FK)
    - confirmed_date, confirmed_time
    - estimated_arrival_time
    - actual_arrival_time
    - actual_departure_time
    - status (scheduled, en_route, arrived, in_progress, completed, no_show)
    - payment_amount
    - payment_status (pending, paid, refunded)
```

**Assignment Algorithm:**
```python
class GuideAssignmentEngine:
    def find_available_guides(service_request):
        """
        Match based on:
        1. Service area (sector proximity)
        2. Required certifications
        3. Availability in requested time slot
        4. Current workload
        5. Rating score
        """
        
    def auto_assign(service_request):
        """Assign best-match guide automatically"""
        
    def notify_guides(guides_list, service_request):
        """Send SMS/WhatsApp to guides, first to accept wins"""
```

**API Endpoints:**
```python
POST /api/v1/service-requests/
GET  /api/v1/service-requests/{id}/available-guides/
POST /api/v1/service-requests/{id}/assign/{guide_id}/
PATCH /api/v1/service-bookings/{id}/status/
```

**Tests:** 60+ tests (matching algorithm, booking flow, status transitions)

### Week 19: Mobile App for Care Guides (React Native)

**Key Features:**
1. **Dashboard**
   - Today's visits
   - Upcoming bookings
   - Earnings summary
   - Rating display

2. **Visit Management**
   - View booking details
   - GPS navigation to patient
   - Check-in/check-out
   - Visit timer

3. **Digital SOP Checklists**
```python
class ServiceSOP:
    - service_type (FK)
    - step_number
    - instruction_kinyarwanda, instruction_english
    - is_critical (Boolean)
    - requires_photo (Boolean)
    - requires_nurse_approval (Boolean)
    
class VisitChecklist:
    - booking (FK)
    - sop (FK)
    - completed_steps (JSON array of step numbers)
    - photos_urls (JSON array)
    - notes (TextField)
    - completed (Boolean)
    - nurse_approved (Boolean)
```

4. **Vitals Capture**
```python
class VitalsReading:
    - booking (FK)
    - patient (FK)
    - recorded_at
    - blood_pressure_systolic, blood_pressure_diastolic
    - heart_rate
    - temperature
    - blood_glucose
    - oxygen_saturation
    - weight
    - notes (TextField)
    - photo_url (for proof/documentation)
    - flagged_as_abnormal (Boolean)
    - nurse_notified (Boolean)
```

5. **Communication**
   - In-app chat with nurse supervisor
   - Emergency button (call nurse directly)
   - SMS patient appointment confirmation

**Tests:** 70+ tests (API, offline sync, photo upload, GPS)

### Week 20: Quality Assurance & Review Workflow

**Models:**
```python
class VisitReview:
    - booking (FK)
    - reviewed_by (nurse FK)
    - review_date
    - checklist_compliance_score (1-5)
    - vitals_accuracy_score (1-5)
    - patient_interaction_score (1-5)
    - documentation_quality_score (1-5)
    - overall_score (calculated)
    - feedback (TextField)
    - requires_followup (Boolean)
    - approved (Boolean)
    
class PatientFeedback:
    - booking (FK)
    - rating (1-5 stars)
    - care_guide_punctuality (1-5)
    - care_guide_professionalism (1-5)
    - care_guide_competence (1-5)
    - would_recommend (Boolean)
    - comments (TextField)
    - submitted_at
```

**Review Workflow:**
```python
@shared_task
def trigger_visit_review(booking_id):
    """After visit completion, assign to nurse for review"""
    
@shared_task
def request_patient_feedback(booking_id):
    """Send SMS requesting feedback 2 hours after visit"""
    
@shared_task
def calculate_guide_ratings():
    """Update care guide rating averages nightly"""
```

**API Endpoints:**
```python
POST /api/v1/nurse/visit-reviews/
GET  /api/v1/nurse/visits/pending-review/
GET  /api/v1/care-guides/{id}/performance-report/
POST /api/v1/patients/feedback/
```

**Tests:** 50+ tests

**Phase 5 Total:** 220+ tests for care guide system

---

## Phase 6: Provider Dashboards (Weeks 21-24)

### Week 21: Hospital Dashboard

**Key Metrics:**
```python
class HospitalDashboard:
    - Total discharged patients (30/60/90 days)
    - Active monitoring patients
    - Medication adherence rate (overall + per patient)
    - Appointment compliance rate
    - Missed follow-ups (actionable list)
    - Readmission rate (30-day)
    - High-risk patients (flagged alerts)
    - Cost savings estimate
```

**Views/Widgets:**
1. **Patient List**
   - Filterable by risk level, adherence, last contact
   - Color-coded status indicators
   - Quick actions (send message, schedule call)

2. **Adherence Trends**
   - Line charts over time
   - Comparison by condition type
   - Best/worst performers

3. **Alerts Feed**
   - Real-time red flags
   - Overdue follow-ups
   - Concerning adherence drops

4. **Discharge Summary**
   - Bulk export
   - Share with other providers
   - Print reports

**API Endpoints:**
```python
GET /api/v1/hospitals/{id}/dashboard/summary/
GET /api/v1/hospitals/{id}/patients/?risk_level=high
GET /api/v1/hospitals/{id}/adherence-trends/?period=month
GET /api/v1/hospitals/{id}/readmissions/
GET /api/v1/hospitals/{id}/cost-savings/
```

**Tests:** 50+ tests

### Week 22: Insurance Dashboard (RSSB/Mutuelle)

**Key Metrics:**
```python
class InsuranceDashboard:
    - Total patients enrolled in BiCare360
    - Prevented readmissions (estimated)
    - Cost savings (RWF)
    - High-cost patient early interventions
    - Chronic disease management outcomes
    - Medication adherence impact on claims
```

**Views:**
1. **Cost Savings Analysis**
   - Readmission prevention value
   - Emergency visit reduction
   - Medication adherence impact on complications

2. **Risk Stratification**
   - High-risk patients receiving proactive care
   - Predicted vs actual utilization

3. **Outcome Metrics**
   - Blood pressure control rates
   - Diabetes management (HbA1c tracking)
   - Hospital length of stay trends

**Models:**
```python
class CostSavingEvent:
    - patient (FK)
    - event_type (readmission_prevented, er_visit_avoided, complication_prevented)
    - estimated_cost_saved (RWF)
    - date_identified
    - basis (TextField: "Patient flagged with chest pain, nurse intervened")
    - verified_by (medical director)
    
class InsuranceReport:
    - insurance_provider (RSSB, Mutuelle)
    - report_period (month, quarter)
    - total_patients_monitored
    - adherence_rate_overall
    - readmissions_prevented_count
    - total_cost_savings
    - generated_at
```

**API Endpoints:**
```python
GET /api/v1/insurance/dashboard/summary/
GET /api/v1/insurance/cost-savings/?start_date=2026-01-01
GET /api/v1/insurance/reports/quarterly/
GET /api/v1/insurance/high-risk-patients/
```

**Tests:** 45+ tests

### Week 23: Analytics Engine & Predictive Models

**Machine Learning Models:**
```python
class PredictiveModel:
    - model_type (readmission_risk, adherence_prediction, appointment_no_show)
    - version
    - accuracy_score
    - trained_date
    - feature_importance (JSON)
    - is_active (Boolean)
    
class PatientRiskScore:
    - patient (FK)
    - model_used (FK)
    - risk_score (0-100)
    - risk_category (low, medium, high)
    - contributing_factors (JSON)
    - calculated_at
    - valid_until
```

**Features for Readmission Prediction:**
- Age, gender, chronic conditions
- Discharge diagnosis severity
- Medication adherence rate
- Missed appointments count
- Social determinants (distance from hospital, phone ownership)
- Previous readmissions

**ML Pipeline:**
```python
@shared_task
def train_readmission_model():
    """Monthly retraining with latest data"""
    
@shared_task
def calculate_patient_risk_scores():
    """Weekly scoring for all active patients"""
    
@shared_task
def identify_high_risk_patients():
    """Daily check, alert care team for scores >80"""
```

**Tests:** 40+ tests

### Week 24: Data Export & Integration APIs

**Interoperability:**
```python
class DataExport:
    - exported_by (user FK)
    - export_type (patient_data, adherence_report, outcomes_report)
    - format (CSV, JSON, HL7, FHIR)
    - filters (JSON)
    - file_url
    - generated_at
    - expires_at
    
# Integration APIs for EMR systems
class EMRIntegration:
    - hospital (FK)
    - emr_system (OpenMRS, DHIS2, custom)
    - api_endpoint
    - auth_type (API key, OAuth)
    - last_sync_at
    - sync_frequency
    - is_active
```

**API Endpoints (for external systems):**
```python
# Public APIs (with auth)
GET  /api/v1/integrations/patient/{national_id}/summary/
POST /api/v1/integrations/discharge/import/
GET  /api/v1/integrations/adherence-report/{patient_id}/
POST /webhook/emr/discharge-notification/
```

**Tests:** 45+ tests

**Phase 6 Total:** 180+ tests for dashboards

---

## Phase 7: USSD for Feature Phones (Weeks 25-26)

### Week 25: USSD Gateway Integration

**Setup:**
- Partner with MTN Rwanda / Airtel
- Get USSD short code (e.g., *888#)

**USSD Flow:**
```
Dial *888#

1. Medication Reminders
2. Appointments
3. Talk to Nurse
4. Health Tips

[User selects 1]

Your Medications:
1. Blood pressure pill (8 AM daily)
2. Diabetes medication (2x daily)

[User selects 1]

Did you take it today?
1. Yes
2. No
3. Skip

[User selects 1]

Thank you! Keep it up!
Next reminder: Tomorrow 8 AM
```

**Models:**
```python
class USSDSession:
    - session_id (from gateway)
    - phone_number
    - patient (FK, nullable)
    - started_at, ended_at
    - menu_path (JSON: [main, medications, log])
    - current_menu
    - user_inputs (JSON)
    
class USSDMenu:
    - menu_key (main, medications, appointments, etc.)
    - title_kinyarwanda, title_english
    - options (JSON array)
    - handler_function
```

**Implementation:**
```python
@api_view(['POST'])
def ussd_handler(request):
    """
    Handle USSD requests:
    - Parse session, phone, input
    - Determine menu state
    - Execute business logic
    - Return formatted response
    """
    
class USSDService:
    def handle_medication_menu(session):
        """Show medications, log adherence"""
        
    def handle_appointment_menu(session):
        """Show upcoming, confirm attendance"""
        
    def handle_nurse_request(session):
        """Create callback request for nurse"""
```

**Tests:** 55+ tests

### Week 26: Offline Support & Fallback Mechanisms

**SMS Fallback:**
- If USSD unavailable, fallback to SMS menu
- Basic commands via keywords: "MEDS", "APPT", "HELP"

**Voice Call IVR:**
- For elderly or illiterate patients
- Pre-recorded messages in Kinyarwanda
- Touch-tone responses

**Tests:** 35+ tests

**Phase 7 Total:** 90+ tests for USSD

---

## Phase 8: Frontend Applications (Weeks 27-32)

### Weeks 27-28: React Admin Dashboard

**Tech Stack:**
- React 18, TypeScript
- Tailwind CSS + shadcn/ui
- React Query (data fetching)
- Recharts (visualizations)
- WebSocket (real-time)

**Key Pages:**
1. Login / Dashboard home
2. Patient list & detail view
3. Discharge summary form
4. Medication management
5. Appointment calendar
6. Alert management (nurse console)
7. Care guide management
8. Analytics & reports

**Tests:** E2E tests with Playwright

### Weeks 29-30: React Native Mobile App (Patients & Families)

**Features:**
1. Profile & consent management
2. Medication reminders & logging
3. Appointment calendar
4. AI chatbot
5. Request care guide visit
6. Vitals history
7. Hospital contact
8. Emergency button

**Offline Support:**
- Local SQLite storage
- Sync when online
- Queue actions

**Tests:** E2E tests with Detox

### Weeks 31-32: Care Guide Mobile App (Polish & Production Deploy)

**Final Features:**
- Push notifications
- Background GPS tracking
- Photo compression
- Offline mode (full functionality)
- Payment integration

**Production Deployment:**
- Docker containers
- Kubernetes orchestration
- CI/CD with GitHub Actions
- SSL certificates
- Domain setup
- Monitoring (Sentry, DataDog)

---

## Testing Strategy

### Coverage Requirements
- **Minimum:** 95% per module
- **Target:** 97%+ overall
- **Critical paths:** 100% (payment, alerts, medication reminders)

### Test Types Distribution
- **Unit Tests:** 60%
- **Integration Tests:** 25%
- **E2E Tests:** 10%
- **Manual Tests:** 5%

### Total Estimated Tests: **1,100+ tests**
- Phase 1: 130 tests
- Phase 2: 150 tests
- Phase 3: 195 tests
- Phase 4: 190 tests
- Phase 5: 220 tests
- Phase 6: 180 tests
- Phase 7: 90 tests
- Phase 8: 150 tests (E2E)

---

## Infrastructure & DevOps

### Production Stack
```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg15
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
  django:
    build: ./backend
    depends_on: [postgres, redis]
    environment:
      - DJANGO_SETTINGS_MODULE=bicare360.settings.prod
      
  celery:
    build: ./backend
    command: celery -A bicare360 worker -l info
    
  celery-beat:
    build: ./backend
    command: celery -A bicare360 beat -l info
    
  nginx:
    image: nginx:alpine
    ports: [80:80, 443:443]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest --cov --cov-fail-under=95
        
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: kubectl apply -f k8s/
```

---

## Budget & Resources

### Team Requirements
- **Backend Engineers:** 2 (Python/Django)
- **Frontend Engineers:** 2 (React/React Native)
- **AI/ML Engineer:** 1 (NLP, RAG)
- **DevOps Engineer:** 1
- **QA Engineer:** 1
- **Medical Advisor:** 1 (part-time)
- **Product Manager:** 1

### External Services (Monthly Costs)
- **Africa's Talking:** $500-1000 (SMS/USSD)
- **WhatsApp Business:** $0.005-0.01 per message
- **AI API (OpenAI/Anthropic):** $500-2000
- **AWS/Digital Ocean:** $500-1000
- **Domain & SSL:** $50
- **Monitoring (Sentry, DataDog):** $200
- **Total:** $2,000-5,000/month

### Timeline Summary
- **Development:** 32 weeks (8 months)
- **MVP (Phases 1-4):** 16 weeks (4 months)
- **Full System:** 32 weeks (8 months)
- **Hospital Pilot:** Month 5
- **Beta Launch:** Month 7
- **Public Launch:** Month 9

---

## Success Metrics

### Phase 1-4 (MVP)
- ✅ 500+ patients enrolled in pilot
- ✅ 95%+ test coverage maintained
- ✅ 80%+ medication adherence rate
- ✅ <15 minute average nurse response time
- ✅ 30% reduction in missed follow-ups

### Phases 5-8 (Full System)
- ✅ 5,000+ patients across 5 hospitals
- ✅ 100+ active care guides
- ✅ 20% reduction in 30-day readmissions
- ✅ $500,000+ documented cost savings
- ✅ 90%+ patient satisfaction

---

## Risk Mitigation

### Technical Risks
- **SMS delivery failures:** Fallback to WhatsApp, implement retry logic
- **AI hallucinations:** Strict RAG grounding, nurse review layer
- **Data loss:** Daily backups, point-in-time recovery
- **Downtime:** 99.9% SLA, redundant servers, health checks

### Operational Risks
- **Low patient adoption:** Train CHWs, incentivize enrollment
- **Nurse burnout:** Proper staffing ratios, shift management
- **Care guide quality:** Rigorous vetting, ongoing training
- **Data privacy breach:** Encryption, access controls, audits

### Regulatory Risks
- **Lack of medical licensing:** Partner with licensed hospitals
- **Insurance non-adoption:** Pilot with data, show ROI
- **Telemedicine restrictions:** Consult Rwanda MoH early

---

## Next Steps - This Week

### Immediate Actions (Week 1)
1. ✅ Set up Africa's Talking account
2. ✅ Create DischargeSummary model
3. ✅ Create Medication model
4. ✅ Create Appointment model
5. ✅ Create Consent model
6. ✅ Write 40+ tests for new models
7. ✅ Update API documentation

**Let's start building the real BiCare360!** 🚀

Ready to begin Week 1 (Discharge Summary & Hospital Integration)?
