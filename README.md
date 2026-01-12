# BiCare360 🏥

**AI-Powered Healthcare Platform for Rwanda**

[![Test Coverage](https://img.shields.io/badge/coverage-96.42%25-brightgreen.svg)](backend/TEST_SUMMARY.md)
[![Tests](https://img.shields.io/badge/tests-131%20passing-brightgreen.svg)](backend/TEST_SUMMARY.md)
[![Django](https://img.shields.io/badge/Django-4.2.9-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14.0-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)

BiCare360 is a comprehensive healthcare management platform designed specifically for Rwanda's healthcare system, featuring AI-powered triage, multi-language support, and real-time patient care coordination.

---

## 🎯 Project Overview

BiCare360 bridges the gap between patients and healthcare providers in Rwanda through:

- 🏥 **Patient Enrollment** - Rwanda-specific validation (national ID, phone numbers)
- 🔍 **AI-Powered Triage** - Intelligent symptom assessment and priority scoring
- 💬 **Multi-Channel Messaging** - SMS, WhatsApp integration for patient communication
- 📊 **Care Planning** - Comprehensive care plan management and tracking
- 🤖 **RAG AI Assistant** - Context-aware medical guidance using PGVector
- 🌍 **Multi-Language** - Kinyarwanda, English, and French support

---

## 📊 Current Status

### Phase 1: Patient Enrollment API ✅ COMPLETE

| Metric | Status |
|--------|--------|
| **Development Phase** | Phase 1 of 6 ✅ |
| **Test Coverage** | 96.42% (exceeds 95% requirement) |
| **Total Tests** | 131 passing |
| **Code Quality** | Production-ready |
| **Documentation** | Comprehensive |

---

## 🚀 Features

### ✅ Phase 1: Patient Enrollment (COMPLETE)

- **Patient Management**
  - Complete CRUD operations
  - Rwanda 16-digit national ID validation
  - +250 phone number format enforcement
  - Multi-language name support (Kinyarwanda/English/French)
  - Soft delete with activate/deactivate actions

- **Address Management**
  - Rwanda 5-level administrative structure (Province → District → Sector → Cell → Village)
  - GPS coordinate support with validation
  - Location-based filtering

- **Emergency Contacts**
  - Multiple contacts per patient
  - Primary contact designation
  - Relationship tracking

- **API Features**
  - RESTful API with Django REST Framework
  - JWT authentication ready
  - Pagination, filtering, searching, ordering
  - Swagger/ReDoc documentation
  - Query optimization (N+1 prevention)

### 🔄 Phase 2: Care Plan Management (In Progress)
- Care plan creation and tracking
- Activity scheduling and monitoring
- Progress reporting
- Provider coordination

### 📋 Phase 3: Triage & Assessment (Planned)
- AI-powered symptom checker
- Priority scoring algorithm
- Assessment workflows
- Medical history integration

### 💬 Phase 4: Messaging System (Planned)
- SMS integration (Twilio)
- WhatsApp Business API
- Automated notifications
- Two-way communication

### 🤖 Phase 5: AI/RAG Integration (Planned)
- PGVector document embeddings
- Semantic search capabilities
- AI-powered recommendations
- Medical knowledge base

### 📱 Phase 6: Frontend Applications (Planned)
- React admin dashboard
- React Native mobile app
- PWA for offline support
- E2E testing

---

## 🏗️ Architecture

```
BiCare360/
├── backend/                    # Django REST API
│   ├── apps/
│   │   └── patients/          # Patient enrollment module ✅
│   │       ├── models.py      # Patient, Address, EmergencyContact
│   │       ├── serializers.py # DRF serializers
│   │       ├── views.py       # API ViewSets
│   │       └── tests/         # 131 comprehensive tests
│   ├── bicare360/
│   │   └── settings/          # Split settings (dev/test/prod)
│   ├── requirements/          # Dependency management
│   └── docs/                  # API documentation
│
├── frontend/                  # React admin dashboard (Coming Soon)
├── mobile/                    # React Native app (Coming Soon)
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
