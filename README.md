# BiCare360 🏥

**Post-Discharge Healthcare Management System for Rwanda**

[![Test Coverage](https://img.shields.io/badge/coverage-96.74%25-brightgreen.svg)](backend/TEST_SUMMARY.md)
[![Tests](https://img.shields.io/badge/tests-185%20passing-brightgreen.svg)](backend/TEST_SUMMARY.md)
[![Django](https://img.shields.io/badge/Django-4.2.9-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14.0-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)

## 🎯 What We're Building

BiCare360 is a **comprehensive healthcare management system** specifically designed for Rwanda's healthcare system. We're building a "Hybrid Care Bridge" that ensures patients never feel lost after hospital discharge by combining AI-powered automation with human care coordination.

**Core Problem:** In Rwanda and across Africa, patients are often discharged from hospitals with minimal follow-up support, leading to medication non-adherence, missed appointments, and preventable readmissions.

**Our Solution:** A complete care coordination platform that bridges the gap between hospital and home through:

### The "Hybrid Care Bridge" Components:

1. 🏥 **Bedside Hand-off** ✅ *Week 1 Complete*
   - Hospital registration and EMR integration tracking
   - Comprehensive discharge summary capture with ICD-10 coding
   - Risk assessment (low/medium/high/critical)
   - Bilingual instructions (English + Kinyarwanda)

2. 👤 **Patient Management** ✅ *Phase 1 Basic Complete*
   - Rwanda national ID validation (16 digits)
   - Phone number validation (+250 format)
   - Address with Rwanda administrative structure
   - Emergency contacts

3. 💊 **Medication Management** 🔄 *Week 2 - In Progress*
   - Prescription tracking from discharge
   - Adherence monitoring
   - SMS reminders for medication schedules

4. 💬 **24/7 Digital Companion** 📋 *Phases 2-3 Planned*
   - SMS/WhatsApp integration (Africa's Talking)
   - AI chatbot with RAG in Kinyarwanda
   - Automated patient check-ins

5. 👩‍⚕️ **Nurse Triage System** 📋 *Phase 4 Planned*
   - Alert engine with 10-minute response SLA
   - Nurse console dashboard
   - Escalation workflows

6. 🤝 **Abafasha Care Guides** 📋 *Phase 5 Planned*
   - Mobile app for care coordinators
   - In-person visit scheduling
   - Patient feedback collection

7. 📊 **Provider Dashboards** 📋 *Phases 6-8 Planned*
   - Hospital performance analytics
   - Insurance/RSSB integration
   - Cost savings reporting

---

## 📍 Current Development Stage

**Timeline:** 32-week implementation (8 months)  
**Current Progress:** Week 1 of 32 (3.125% complete)  
**Current Phase:** Phase 1 - Foundation & Discharge Management  
**Status:** Week 1 ✅ Complete, Week 2 🔄 Starting

### What's Been Built (Week 1):
- ✅ Hospital registration system
- ✅ Discharge summary capture with risk assessment
- ✅ Patient enrollment API
- ✅ 185 comprehensive tests (96.74% coverage)
- ✅ Django admin interfaces
- ✅ API documentation (Swagger/ReDoc)

### What's Next (Weeks 2-4):
- 🔄 Week 2: Medication catalog, prescriptions, adherence tracking
- 📋 Week 3: Appointment scheduling with SMS reminders
- 📋 Week 4: Consent management and GDPR compliance

---

## 📊 Current Status

### Phase 1: Foundation & Discharge Management (Week 1/4 Complete)

| Metric | Status |
|--------|--------|
| **Development Phase** | Week 1 of 32 ✅ (3.125% complete) |
| **Test Coverage** | 96.74% (exceeds 95% requirement) |
| **Total Tests** | 185 passing (131 patients + 54 enrollment) |
| **Code Quality** | Production-ready |
| **Documentation** | Comprehensive |

---

## 🚀 Features

### ✅ Week 1: Hospital & Discharge Management (COMPLETE)

- **Hospital Registration**
  - Rwanda location structure (province/district/sector)
  - Hospital types (referral/district/health_center/clinic)
  - EMR integration tracking (manual/API/HL7)
  - Phone validation (+250 format)
  - Status management (active/pilot/inactive)

- **Discharge Summary Capture**
  - Comprehensive discharge data with ICD-10 coding
  - Auto-calculated: length_of_stay, days_since_discharge, is_high_risk
  - Risk assessment (low/medium/high/critical)
  - Bilingual: English + Kinyarwanda (instructions/warnings)
  - Follow-up requirements tracking
  - Provider information (attending physician, discharge nurse)

- **Custom Endpoints**
  - `/high_risk/` - High/critical risk patients
  - `/recent/?days=7` - Recent discharges
  - `/needs_follow_up/` - Requires follow-up
  - `/{id}/risk_analysis/` - Detailed risk assessment

- **Patient Management** (From Phase 1 Basic)
  - Complete CRUD operations
  - Rwanda 16-digit national ID validation
  - +250 phone number format enforcement
  - Multi-language support (Kinyarwanda/English/French)
  - Address management with Rwanda admin structure
  - Emergency contacts tracking

### 🔄 Week 2-4: Medication & Appointments (Weeks 2-4 of Phase 1)
- Week 2: Medication catalog, prescriptions, adherence tracking
- Week 3: Appointment scheduling with reminders
- Week 4: Consent management and data privacy

### 📋 Phase 2: SMS/WhatsApp Messaging (Weeks 5-8)
- Africa's Talking SMS integration
- WhatsApp Business API
- Kinyarwanda message templates
- Automated adherence reminders
- Two-way communication

### 🤖 Phase 3: AI Chatbot with RAG (Weeks 9-12)
- PGVector embeddings for medical knowledge
- Kinyarwanda NLP support
- Symptom checker with red flags
- Context-aware responses
- Automatic escalation to nurses

### 👩‍⚕️ Phase 4: Nurse Triage System (Weeks 13-16)
- Alert engine with risk scoring
- 10-minute response SLA tracking
- Nurse console dashboard
- Patient communication tools
- Escalation workflows

### 🤝 Phase 5: Abafasha Care Guides (Weeks 17-20)
- Care guide mobile app
- Task assignment and tracking
- In-person visit scheduling
- Patient feedback collection
- Performance metrics

### 📊 Phase 6-8: Dashboards & Production (Weeks 21-32)
- Hospital provider dashboards
- Insurance/RSSB analytics
- USSD fallback for feature phones
- React Native patient app
- Full production deployment

---

## 🏗️ Architecture

```
BiCare360/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── patients/          # Patient management ✅
│   │   │   ├── models.py      # Patient, Address, EmergencyContact
│   │   │   ├── serializers.py # 5 serializers (89% coverage)
│   │   │   ├── views.py       # 3 ViewSets (100% coverage)
│   │   │   └── tests/         # 131 tests passing
│   │   └── enrollment/        # Discharge & hospital management ✅
│   │       ├── models.py      # Hospital, DischargeSummary (98.67% coverage)
│   │       ├── serializers.py # 4 serializers (95.65% coverage)
│   │       ├── views.py       # 2 ViewSets (97.53% coverage)
│   │       ├── admin.py       # Django admin (96.15% coverage)
│   │       └── tests/         # 54 tests passing
│   ├── bicare360/
│   │   └── settings/          # Split settings (dev/test/prod)
│   ├── requirements/          # Dependency management
│   └── htmlcov/               # Coverage reports
│
├── frontend/                  # React admin dashboard (Weeks 27-32)
├── mobile/                    # React Native app (Weeks 27-32)
└── docs/                      # Project documentation

```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.2.9
- **API:** Django REST Framework 3.14.0
- **Database:** PostgreSQL 15+ with PGVector extension
- **Cache/Queue:** Redis 7+
- **Task Queue:** Celery 5.3.6
- **Authentication:** JWT (Simple JWT)
- **Testing:** pytest 8.0.0, factory-boy, Faker

### Frontend (Coming Soon)
- React 18+
- TypeScript
- Tailwind CSS
- React Query

### Mobile (Coming Soon)
- React Native
- Expo
- TypeScript

### DevOps
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- PostgreSQL
- Redis

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Redis 7+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/didier-building/Bicare360.git
cd Bicare360

# Set up backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Run tests to verify setup
pytest apps/patients/tests/ --cov=apps/patients

# Start development server
python manage.py runserver
```

### API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/

---

## 🧪 Testing

BiCare360 follows Test-Driven Development (TDD) with comprehensive test coverage.

```bash
# Run all tests
pytest apps/patients/tests/ -v

# Run with coverage report
pytest apps/patients/tests/ --cov=apps/patients --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Coverage Breakdown

| Module | Coverage | Tests |
|--------|----------|-------|
| Models | 100% | 25 |
| Views | 100% | 27 |
| Serializers | 89.36% | 13 |
| API Integration | 100% | 26 |
| Edge Cases | 100% | 40 |
| **Overall** | **96.42%** | **131** |

For detailed testing information, see [TESTING_GUIDE.md](backend/TESTING_GUIDE.md)

---

## 📖 Documentation

- **[Backend README](backend/README.md)** - Backend setup and API details
- **[Testing Guide](backend/TESTING_GUIDE.md)** - Comprehensive testing documentation
- **[Test Summary](backend/TEST_SUMMARY.md)** - Test execution results
- **API Docs** - Interactive Swagger/ReDoc documentation

---

## 🇷🇼 Rwanda-Specific Features

### National ID Validation
- 16-digit format: `1234567890123456`
- Unique constraint enforced
- Regex validation

### Phone Number Format
- Country code: +250 (Rwanda)
- Format: `+250XXXXXXXXX` (13 characters total)
- Supports SMS and WhatsApp

### Administrative Structure
Rwanda's 5-level hierarchy:
1. **Province** (Intara) - 5 provinces
2. **District** (Akarere) - 30 districts
3. **Sector** (Umurenge) - 416 sectors
4. **Cell** (Akagari) - 2,148 cells
5. **Village** (Umudugudu) - 14,837 villages

### Language Support
- **Kinyarwanda (kin)** - Default, primary language
- **English (eng)** - Official language
- **French (fra)** - Official language

---

## 🔒 Security Features

- ✅ JWT authentication
- ✅ CORS configuration
- ✅ Environment-based secrets
- ✅ Input validation and sanitization
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection
- ✅ HTTPS enforcement (production)
- ✅ Rate limiting (planned)

---

## 📈 Roadmap

### Q1 2026
- ✅ Phase 1: Patient Enrollment API (Complete)
- 🔄 Phase 2: Care Plan Management (In Progress)
- 📋 Phase 3: Triage & Assessment

### Q2 2026
- 📋 Phase 4: Messaging System
- 📋 Phase 5: AI/RAG Integration
- 📋 Phase 6: Frontend Development

### Q3 2026
- 📋 Mobile app development
- 📋 Production deployment
- 📋 User acceptance testing

### Q4 2026
- 📋 Public beta launch
- 📋 Healthcare provider training
- 📋 Nationwide rollout

---

## 🤝 Contributing

BiCare360 is currently in active development. Contributions are welcome!

### Development Workflow

1. **Follow TDD** - Write tests before implementation
2. **Maintain Coverage** - Keep test coverage above 95%
3. **Code Quality** - Follow Django/DRF best practices
4. **Documentation** - Document all API endpoints
5. **Rwanda Context** - Respect local healthcare practices

### Commit Message Convention

```
feat: Add new feature
fix: Bug fix
docs: Documentation update
test: Add or update tests
refactor: Code refactoring
chore: Maintenance tasks
```

---

## 👥 Team

**Project Lead:** Didier  
**Development Team:** BiCare360 Engineering

---

## 📄 License

Proprietary - BiCare360 Healthcare Platform

© 2026 BiCare360. All rights reserved.

---

## 🌟 Acknowledgments

- Rwanda Ministry of Health
- Healthcare providers across Rwanda
- Open-source Django and DRF communities
- Contributors and testers

---

## 📞 Contact & Support

- **GitHub Issues:** [Report bugs or request features](https://github.com/didier-building/Bicare360/issues)
- **Documentation:** [Full documentation](backend/README.md)
- **Email:** support@bicare360.rw (coming soon)

---

## 🎯 Project Goals

BiCare360 aims to:

1. **Improve Access** - Make healthcare accessible to all Rwandans
2. **Enhance Quality** - Provide AI-powered clinical decision support
3. **Reduce Wait Times** - Intelligent triage and appointment scheduling
4. **Enable Communication** - Multi-channel patient-provider messaging
5. **Support Languages** - Native Kinyarwanda alongside English and French
6. **Ensure Privacy** - HIPAA-compliant data protection
7. **Scale Nationally** - Support Rwanda's entire healthcare system

---

**Built with ❤️ for Rwanda's healthcare system**

[![GitHub stars](https://img.shields.io/github/stars/didier-building/Bicare360?style=social)](https://github.com/didier-building/Bicare360)
[![GitHub forks](https://img.shields.io/github/forks/didier-building/Bicare360?style=social)](https://github.com/didier-building/Bicare360/fork)
