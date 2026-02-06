# BiCare360 - Hybrid Home-Care Platform

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**BiCare360** is a comprehensive continuity-of-care platform designed for Rwanda's healthcare ecosystem. It bridges the gap between hospital discharge and home care, enabling seamless coordination between healthcare providers, nurses, caregivers, and patients.

---

## 🎯 Vision & Purpose

Healthcare doesn't end at hospital discharge. BiCare360 ensures patients receive coordinated, continuous care through:

- 🏥 **Hospital Integration** - Automated discharge summary ingestion
- 👨‍⚕️ **Nurse Triage System** - Intelligent alert routing and case management
- 👵 **Home Caregiver Network** - "Abafasha" marketplace for professional home care
- 📱 **Patient Portal** - Bilingual (English/Kinyarwanda) self-service platform
- 💊 **Medication Management** - Prescription tracking and adherence monitoring
- 📅 **Smart Scheduling** - Appointment management with SMS/WhatsApp reminders
- 🔔 **Proactive Alerts** - Early detection of medication non-adherence and missed appointments
- 🇷🇼 **Rwanda-First Design** - National ID integration, administrative structure support, local telecom integration

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Admin   │  │  Nurse   │  │ Patient  │  │Caregiver │        │
│  │Dashboard │  │Dashboard │  │  Portal  │  │  Portal  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │              │              │               │
│       └─────────────┴──────────────┴──────────────┘               │
│                         │                                          │
│              React 18 + TypeScript + Vite                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                   ┌──────▼───────┐
                   │   REST API   │
                   │  (DRF + JWT) │
                   └──────┬───────┘
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                    BACKEND LAYER                                   │
│  ┌────────────────┬────────────────┬────────────────┬───────────┐│
│  │   Users &      │   Patient      │   Clinical     │ External  ││
│  │   Auth         │   Management   │   Operations   │ Services  ││
│  ├────────────────┼────────────────┼────────────────┼───────────┤│
│  │ • users        │ • patients     │ • appointments │ • messaging│
│  │ • authentication│ • enrollment  │ • medications  │ • consents││
│  │ • core         │ • vitals       │ • nursing      │           ││
│  │                │ • caregivers   │                │           ││
│  └────────────────┴────────────────┴────────────────┴───────────┘│
│                                                                    │
│  Django 4.2 + DRF + Celery + Guardian                            │
└────────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────┼───────────────────────────────────────┐
│                    DATA LAYER                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │PostgreSQL│  │  Redis   │  │  Celery  │  │   S3     │         │
│  │ (Primary)│  │  (Cache) │  │  (Tasks) │  │ (Media)  │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
└────────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼───────────────────────────────────────┐
│                 EXTERNAL INTEGRATIONS                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Africa's Talking│  │  Hospital EMRs  │  │  DHIS2 / MOH    │  │
│  │  (SMS/WhatsApp) │  │  (HL7/FHIR)     │  │  (Analytics)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### Application Structure

```
bicare360/
├── backend/                      # Django Backend
│   ├── apps/
│   │   ├── users/               # User management & authentication
│   │   ├── patients/            # Patient records & demographics
│   │   ├── enrollment/          # Hospital integration & discharge summaries
│   │   ├── medications/         # Medication catalog & prescriptions
│   │   ├── appointments/        # Scheduling & reminders
│   │   ├── nursing/             # Nurse triage & alert system
│   │   ├── caregivers/          # Abafasha caregiver management
│   │   ├── consents/            # GDPR compliance & privacy
│   │   ├── messaging/           # SMS/Email/WhatsApp service
│   │   ├── vitals/              # Health metrics tracking
│   │   └── core/                # Shared utilities & permissions
│   ├── bicare360/              # Project settings
│   │   ├── settings/
│   │   │   ├── base.py         # Shared settings
│   │   │   ├── dev.py          # Development settings
│   │   │   ├── prod.py         # Production settings
│   │   │   └── test.py         # Testing settings
│   │   ├── urls.py             # URL routing
│   │   ├── celery.py           # Celery configuration
│   │   └── wsgi.py             # WSGI entry point
│   ├── requirements/
│   │   ├── base.txt            # Core dependencies
│   │   ├── dev.txt             # Development dependencies
│   │   ├── prod.txt            # Production dependencies
│   │   └── testing.txt         # Testing dependencies
│   └── manage.py               # Django management script
│
└── frontend/                    # React Frontend
    ├── src/
    │   ├── pages/              # Route components
    │   │   ├── admin/          # Admin dashboard
    │   │   ├── nurse/          # Nurse triage interface
    │   │   ├── patient/        # Patient portal
    │   │   └── caregiver/      # Caregiver dashboard
    │   ├── components/         # Reusable components
    │   ├── api/                # API client & endpoints
    │   ├── stores/             # Zustand state management
    │   ├── contexts/           # React contexts
    │   └── hooks/              # Custom React hooks
    ├── public/                 # Static assets
    └── package.json            # npm dependencies
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.2+
- **API:** Django REST Framework 3.14+
- **Authentication:** Simple JWT (JWT tokens)
- **Database:** PostgreSQL 14+ (SQLite for development)
- **Cache:** Redis 7+
- **Task Queue:** Celery 5+ with Redis broker
- **API Docs:** DRF Spectacular (OpenAPI 3.0)
- **Permissions:** Django Guardian (object-level permissions)
- **Integrations:** Africa's Talking (SMS/WhatsApp)

### Frontend
- **Framework:** React 18+
- **Language:** TypeScript 5+
- **Build Tool:** Vite 5+
- **State Management:** Zustand
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **UI Components:** Custom component library
- **Forms:** React Hook Form
- **Validation:** Zod

### DevOps & Tools
- **Version Control:** Git
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions (planned)
- **Monitoring:** Sentry (planned)
- **Testing:** pytest (backend), Vitest (frontend)

---

## ✨ Features

### 🏥 Hospital Integration
- Automated discharge summary ingestion (manual, API, HL7)
- Multi-hospital support with individual configurations
- Comprehensive discharge data capture (diagnoses, procedures, medications, follow-up instructions)
- Bilingual discharge instructions (English/Kinyarwanda)

### 👨‍⚕️ Nurse Triage System
- Intelligent alert engine with severity-based prioritization
- SLA tracking (Critical: 10min, High: 30min, Medium: 2hrs, Low: 4hrs)
- Automated nurse assignment based on workload
- Dashboard with real-time metrics
- Alert types: Missed medications, missed appointments, high-risk discharge, symptom reports

### 👵 Caregiver Marketplace
- Professional home caregiver ("Abafasha") profiles
- License verification & background checks
- Rating & review system
- Service catalog (nursing care, companionship, personal care)
- Availability management
- Geolocation-based caregiver matching

### 📱 Patient Portal
- Bilingual interface (English/Kinyarwanda)
- Secure authentication with JWT
- Appointment viewing & requests
- Medication tracking
- Vital signs self-reporting
- Health goal setting & progress tracking
- Educational content access
- Emergency contact management

### 💊 Medication Management
- Comprehensive medication catalog
- Prescription tracking linked to discharge summaries
- Medication adherence monitoring
- Automated refill reminders
- Side effect reporting
- Drug interaction warnings

### 📅 Appointment System
- Flexible appointment types (follow-up, medication review, consultation, routine checkup)
- Multi-channel reminders (SMS, WhatsApp, Email)
- Appointment confirmation & cancellation
- Home visit scheduling
- Telemedicine support
- Provider & department assignment

### 🔔 Smart Alerts & Notifications
- Proactive patient monitoring
- Missed medication alerts
- Missed appointment notifications
- High-risk patient flagging
- Symptom-based escalation
- Multi-channel delivery (SMS, WhatsApp, Email)

### 🔐 GDPR Compliance
- Versioned consent management
- Granular privacy preferences
- Right to data portability (export endpoint)
- Right to be forgotten (anonymization)
- Audit trails for all consent changes
- IP address logging

### 📊 Analytics & Reporting
- Patient enrollment statistics
- Nurse workload metrics
- Appointment adherence rates
- Medication compliance tracking
- Alert response time analysis
- Caregiver performance metrics

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (or SQLite for development)
- Redis 7+ (for Celery)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bicare360.git
   cd bicare360/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python create_hospital_sample_data.py
   python create_patient_sample_data.py
   python create_nursing_sample_data.py
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

9. **Start Celery worker (separate terminal)**
   ```bash
   celery -A bicare360 worker -l info
   ```

10. **Start Celery beat (separate terminal)**
    ```bash
    celery -A bicare360 beat -l info
    ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with backend API URL
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/
   - Admin Panel: http://localhost:8000/admin/

---

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bicare360
# Or for SQLite (development):
# DATABASE_URL=sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Africa's Talking
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key
AFRICASTALKING_SANDBOX=True
AFRICASTALKING_FROM=BiCare360
SMS_DEMO_MODE=True  # Set to False in production

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=BiCare360 <noreply@bicare360.rw>

# JWT
ACCESS_TOKEN_LIFETIME=3600  # 1 hour in seconds
REFRESH_TOKEN_LIFETIME=604800  # 7 days in seconds
```

#### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
```

### Django Settings Files

- **base.py** - Shared settings for all environments
- **dev.py** - Development-specific settings (DEBUG=True, Django Debug Toolbar)
- **prod.py** - Production settings (DEBUG=False, security headers, logging)
- **test.py** - Testing configuration (in-memory database, no external calls)

To use a specific settings file:
```bash
export DJANGO_SETTINGS_MODULE=bicare360.settings.dev
# or
python manage.py runserver --settings=bicare360.settings.prod
```

---

## 📚 API Documentation

### Interactive API Documentation

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/ (if configured)
- **OpenAPI Schema:** http://localhost:8000/api/schema/

### Authentication

All API endpoints require JWT authentication (except registration and login).

**Obtain Token:**
```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Use Token:**
```http
GET /api/v1/patients/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Core Endpoints

#### Patients
```
GET     /api/v1/patients/                 # List patients
POST    /api/v1/patients/                 # Create patient
GET     /api/v1/patients/{id}/            # Get patient details
PATCH   /api/v1/patients/{id}/            # Update patient
GET     /api/v1/patients/me/              # Get current patient (JWT)
PATCH   /api/v1/patients/me/              # Update current patient
GET     /api/v1/patients/search/          # Advanced search
GET     /api/v1/patients/stats/           # Statistics
POST    /api/v1/patients/register/        # Self-registration
POST    /api/v1/patients/login/           # Patient login
```

#### Appointments
```
GET     /api/v1/appointments/             # List appointments
POST    /api/v1/appointments/             # Create appointment
GET     /api/v1/appointments/{id}/        # Get appointment
PATCH   /api/v1/appointments/{id}/        # Update appointment
GET     /api/v1/appointments/upcoming/    # Upcoming appointments
POST    /api/v1/appointments/{id}/confirm/  # Confirm
POST    /api/v1/appointments/{id}/cancel/   # Cancel
```

#### Nursing Alerts
```
GET     /api/v1/nursing/alerts/           # List alerts
POST    /api/v1/nursing/alerts/           # Create alert
PATCH   /api/v1/nursing/alerts/{id}/assign/     # Assign to nurse
PATCH   /api/v1/nursing/alerts/{id}/acknowledge/# Acknowledge
PATCH   /api/v1/nursing/alerts/{id}/resolve/   # Resolve
GET     /api/v1/nursing/dashboard/        # Dashboard stats
```

#### Medications
```
GET     /api/v1/medications/              # List medications
POST    /api/v1/medications/              # Add medication
GET     /api/v1/prescriptions/            # List prescriptions
POST    /api/v1/prescriptions/            # Create prescription
```

#### Caregivers
```
GET     /api/v1/caregivers/               # List caregivers
POST    /api/v1/caregivers/               # Register caregiver
GET     /api/v1/caregivers/{id}/          # Get caregiver
GET     /api/v1/caregivers/available/     # Available caregivers
```

#### Vitals
```
GET     /api/v1/patients/{id}/vitals/     # List vitals
POST    /api/v1/patients/{id}/vitals/     # Record vitals
GET     /api/v1/patients/{id}/health-goals/  # Health goals
POST    /api/v1/patients/{id}/health-goals/  # Create goal
```

### Filtering, Searching & Pagination

**Filtering:**
```
GET /api/v1/patients/?is_active=true&gender=M
```

**Searching:**
```
GET /api/v1/patients/?search=john
```

**Ordering:**
```
GET /api/v1/patients/?ordering=-enrolled_date
```

**Pagination:**
```
GET /api/v1/patients/?page=2&page_size=50
```

---

## 🗄️ Database Schema

### Core Models

#### Patient
- Demographics (name, DOB, gender, blood type)
- Rwanda National ID (16 digits, unique)
- Contact (phone, email, alt phone)
- Address (province, district, sector, cell, village, GPS)
- Emergency contacts
- Language preference (Kinyarwanda, English, French)
- SMS/WhatsApp preferences
- User account link (for portal access)

#### DischargeSummary
- Hospital & patient references
- Admission & discharge dates
- Diagnoses (primary, secondary, ICD-10 codes)
- Procedures performed
- Treatment summary
- Discharge condition & instructions
- Diet instructions
- Follow-up plan
- Linked prescriptions

#### Appointment
- Patient & hospital references
- Date/time
- Type (follow-up, medication review, consultation, emergency, routine checkup)
- Status (scheduled, confirmed, completed, cancelled, no_show, rescheduled)
- Location type (hospital, home visit, telemedicine)
- Provider & department
- Reason & notes (bilingual)
- Cancellation tracking

#### PatientAlert
- Patient reference
- Alert type (missed medication, missed appointment, high-risk discharge, symptom report, readmission risk)
- Severity (low, medium, high, critical)
- Status (new, assigned, in_progress, resolved, escalated, closed)
- Assigned nurse
- SLA tracking (created, acknowledged, resolved times)
- Related discharge summary or appointment

#### Prescription
- Patient & discharge summary
- Medication reference
- Dosage, frequency, route
- Start & end dates
- Duration & quantity
- Refills allowed
- Special instructions (bilingual)
- Prescriber information

#### Caregiver
- Basic info (name, email, phone)
- Professional info (profession, license, experience)
- Location (province, district, sector)
- Pricing (hourly rate)
- Availability status
- Rating & reviews
- Verification status (background check)

### Relationships

```
Patient (1) ──< (N) DischargeSummary
Patient (1) ──< (N) Appointment
Patient (1) ──< (N) PatientAlert
Patient (1) ──< (N) Prescription
Patient (1) ──< (N) Consent
Patient (1) ──< (N) VitalReading
Patient (1) ─── (1) PrivacyPreference
Patient (1) ─── (1) Address

DischargeSummary (1) ──< (N) Prescription
DischargeSummary (1) ──< (N) Appointment (follow-ups)
DischargeSummary (1) ──< (N) PatientAlert

Hospital (1) ──< (N) DischargeSummary
Hospital (1) ──< (N) Appointment

NurseProfile (1) ──< (N) PatientAlert (assigned)
NurseProfile (1) ──< (N) NursePatientAssignment
```

---

## 🧪 Development

### Code Style

**Backend (Python):**
- Follow PEP 8
- Use Black formatter
- Use isort for imports
- Use flake8 for linting
- Type hints encouraged

**Frontend (TypeScript):**
- ESLint configuration
- Prettier formatting
- Strict TypeScript mode
- React best practices

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

`.pre-commit-config.yaml` includes:
- Black formatting
- isort import sorting
- flake8 linting
- Trailing whitespace removal
- YAML validation

### Database Migrations

**Create migration:**
```bash
python manage.py makemigrations
python manage.py makemigrations app_name  # For specific app
```

**Apply migrations:**
```bash
python manage.py migrate
python manage.py migrate app_name  # For specific app
```

**Revert migration:**
```bash
python manage.py migrate app_name migration_name
```

### Django Management Commands

**Create demo data:**
```bash
python create_hospital_sample_data.py
python create_patient_sample_data.py
python create_nursing_sample_data.py
```

**Create nurse user:**
```bash
python create_demo_nurse_user.py
```

**Django shell:**
```bash
python manage.py shell
# or with IPython:
python manage.py shell_plus
```

---

## 🧪 Testing

### Backend Testing

**Run all tests:**
```bash
pytest
```

**Run specific app:**
```bash
pytest apps/patients/tests/
```

**Run with coverage:**
```bash
pytest --cov=apps --cov-report=html
```

**Run specific test:**
```bash
pytest apps/patients/tests/test_models.py::test_patient_creation
```

### Frontend Testing

**Run all tests:**
```bash
npm test
```

**Run with coverage:**
```bash
npm run test:coverage
```

**Run specific test file:**
```bash
npm test -- PatientList.test.tsx
```

### Test Structure

**Backend:**
```
apps/app_name/tests/
├── __init__.py
├── test_models.py      # Model tests
├── test_views.py       # View/API tests
├── test_serializers.py # Serializer tests
├── factories.py        # Factory Boy factories
└── conftest.py         # Pytest fixtures
```

**Frontend:**
```
src/components/ComponentName/
├── ComponentName.tsx
├── ComponentName.test.tsx
└── ComponentName.stories.tsx  # Storybook (if using)
```

---

## 🚀 Deployment

### Docker Deployment

**Build images:**
```bash
docker-compose build
```

**Start services:**
```bash
docker-compose up -d
```

**Run migrations:**
```bash
docker-compose exec backend python manage.py migrate
```

**Create superuser:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery
```

### Production Checklist

- [ ] Set `DEBUG=False` in production settings
- [ ] Use strong `SECRET_KEY`
- [ ] Configure PostgreSQL (not SQLite)
- [ ] Set up Redis for caching and Celery
- [ ] Configure HTTPS/SSL
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Configure CORS properly
- [ ] Set up static file serving (Whitenoise or CDN)
- [ ] Set up media file storage (S3 or similar)
- [ ] Configure email backend (not console)
- [ ] Set up SMS service (Africa's Talking with real API key)
- [ ] Set `SMS_DEMO_MODE=False`
- [ ] Configure logging (file + external service like Sentry)
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Set up monitoring & alerting
- [ ] Configure firewall rules
- [ ] Set up CI/CD pipeline
- [ ] Run security audit

### Environment-Specific Settings

**Development:**
```bash
export DJANGO_SETTINGS_MODULE=bicare360.settings.dev
```

**Production:**
```bash
export DJANGO_SETTINGS_MODULE=bicare360.settings.prod
```

**Testing:**
```bash
export DJANGO_SETTINGS_MODULE=bicare360.settings.test
```

---

## 🔐 Security

### Security Features

- JWT authentication with token rotation
- Token blacklisting on logout
- Password hashing (Django's PBKDF2)
- CORS configuration
- CSRF protection (Django middleware)
- SQL injection protection (Django ORM)
- XSS protection (Django template escaping)
- HTTPS enforcement (production)
- Object-level permissions (Guardian)
- Audit logging for sensitive operations
- IP address logging for consents
- GDPR compliance features

### Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Keep dependencies updated** - Run `pip list --outdated` regularly
3. **Use HTTPS** in production
4. **Implement rate limiting** on authentication endpoints
5. **Monitor for suspicious activity**
6. **Regular security audits**
7. **Input validation** on all user inputs
8. **Output encoding** to prevent XSS
9. **Parameterized queries** (Django ORM handles this)
10. **Regular backups** with encryption

### Known Security Issues (To Fix)

1. **JWT Blacklist not enabled** - `rest_framework_simplejwt.token_blacklist` not in INSTALLED_APPS
2. **No rate limiting** on authentication endpoints
3. **Password validators** not used in user views
4. **SMS_DEMO_MODE default is True** - Should be False in production

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Write/update tests
5. Ensure tests pass: `pytest` and `npm test`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Review Process

1. All PRs require at least one review
2. All tests must pass
3. Code coverage should not decrease
4. Follow existing code style
5. Update documentation if needed
6. Add changelog entry

### Reporting Issues

When reporting issues, please include:
- Environment (OS, Python version, Node version)
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Screenshots (if applicable)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Project Lead:** [Your Name]  
**Backend Developer:** [Name]  
**Frontend Developer:** [Name]  
**DevOps Engineer:** [Name]

---

## 📞 Support

- **Email:** support@bicare360.rw
- **Documentation:** https://docs.bicare360.rw
- **Issue Tracker:** https://github.com/yourusername/bicare360/issues

---

## 🙏 Acknowledgments

- Rwanda Ministry of Health
- Participating hospitals and health centers
- Africa's Talking for SMS/WhatsApp integration
- Open-source community

---

## 📊 Project Status

**Current Version:** 1.0.0-alpha  
**Status:** Active Development  
**Last Updated:** February 2026

### Roadmap

**v1.0 (Q1 2026) - MVP Launch**
- ✅ Patient enrollment
- ✅ Discharge summary management
- ✅ Nurse triage system
- ✅ Appointment scheduling
- ✅ Medication tracking
- ✅ Patient portal
- ⏳ Caregiver marketplace
- ⏳ SMS/WhatsApp integration

**v1.1 (Q2 2026) - Enhanced Features**
- Mobile apps (iOS/Android)
- Telemedicine integration
- Advanced analytics dashboard
- Hospital EMR integrations
- DHIS2 integration

**v2.0 (Q3 2026) - Scale**
- AI-powered risk prediction
- Voice-based patient interaction (Kinyarwanda)
- Offline-first mobile apps
- Multi-country support

---

## 🌍 Rwanda-Specific Features

- **National ID Validation:** 16-digit Rwanda National ID support
- **Administrative Structure:** Province → District → Sector → Cell → Village
- **Bilingual Support:** English and Kinyarwanda throughout
- **Local Phone Format:** +250XXXXXXXXX validation
- **Africa's Talking Integration:** SMS/WhatsApp via Rwandan telecoms
- **CBHI Integration (Planned):** Community-Based Health Insurance
- **MOH Reporting (Planned):** Ministry of Health data reporting
- **DHIS2 Integration (Planned):** Health information system integration

---

**Built with ❤️ for Rwanda's Healthcare System**
