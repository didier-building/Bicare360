# BiCare 360 Backend

Django REST API backend for BiCare 360 - AI-powered healthcare platform for Rwanda.

## 🎯 Project Status

**Current Phase:** Phase 1 - Patient Enrollment API ✅ COMPLETE  
**Test Coverage:** 96.42% (exceeds 95% requirement)  
**Total Tests:** 131 tests passing  
**Development Approach:** Test-Driven Development (TDD)

## 📊 Test Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Tests** | 131 | ✅ All Passing |
| **Coverage** | 96.42% | ✅ Above 95% |
| **Statements** | 237 | 5 missing |
| **Unit Tests** | 38 | ✅ Passing |
| **Integration Tests** | 26 | ✅ Passing |
| **View Tests** | 27 | ✅ Passing |
| **Edge Case Tests** | 40 | ✅ Passing |

## 🚀 Phase 1 Completion Summary

### ✅ Completed Components

#### 1. Project Infrastructure
- Django 4.2.9 project with split settings (dev/test/prod)
- PostgreSQL support with PGVector extension ready
- Testing infrastructure: pytest 8.0.0, pytest-django, factory-boy, coverage
- Requirements organized by environment (base, dev, testing, prod)
- Pre-commit hooks configured (black, isort, flake8)
- **Coverage threshold: 95% enforced**

#### 2. Patient Models ✅ (TDD Approach)
**Test Coverage: 100%** 🎯

**Models Implemented:**
- `Patient`: Core patient model with Rwanda-specific features
  - National ID validation (16 digits)
  - Rwanda phone number format (+250XXXXXXXXX)
  - Kinyarwanda name support
  - Multi-channel preferences (SMS/WhatsApp/USSD)
  - Language preference (Kinyarwanda/English/French)
  - Blood type, gender, DOB
  - Age calculation property

- `Address`: Rwanda administrative structure
  - Province → District → Sector → Cell → Village
  - GPS coordinates for field visits
  - Landmarks for navigation

- `EmergencyContact`: Multiple contacts per patient
  - Relationship tracking
  - Primary contact flagging
  - Rwanda phone validation

**Test Suite:**
- 25 comprehensive tests
- All passing ✅
- 100% code coverage
- Follows TDD principles (tests written first)

#### 3. Test Factories ✅
- `PatientFactory`: Realistic patient data generation
- `AddressFactory`: Rwanda location data
- `EmergencyContactFactory`: Contact generation
- `UserFactory`: Staff/nurse user creation

### Key Features Implemented

1. **Rwanda-Specific Validation**
   - 16-digit National ID format
   - +250 phone number validation
   - Administrative structure (Province → Village)

2. **Multi-Language Support**
   - Kinyarwanda (default)
   - English
   - French
   - Separate Kinyarwanda name fields

3. **Multi-Channel Communication**
   - SMS preference flag
   - WhatsApp preference flag
   - Prepared for USSD integration

4. **Clinical Safety Foundations**
   - Audit trails (enrolled_by, enrolled_date)
   - Soft delete support (is_active flag)
   - Emergency contact system

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all Patient model tests
ENVIRONMENT=test pytest apps/patients/tests/test_models.py -v

# Run with coverage report
ENVIRONMENT=test pytest apps/patients/tests/test_models.py -v --cov=apps.patients --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

### Test Results
```
25 passed in 2.02s
Coverage: 100.00% ✅
```

### Next Steps (Phase 1 Continuation)

1. **Patient API Implementation** (Day 6-8)
   - DRF Serializers for all models
   - ViewSets with CRUD operations
   - URL routing
   - API tests (targeting 95%+ coverage)

2. **Authentication & Authorization** (Day 9-10)
   - JWT authentication
   - Role-based permissions (Nurse, Admin)
   - Audit logging middleware
   - Auth tests

3. **Phase 1 Completion** (Day 10)
   - Full integration tests
   - Coverage report validation (95%+ gate)
   - API documentation (drf-spectacular)
   - Review & refactor

### Project Structure
```
backend/
├── apps/
│   └── patients/
│       ├── models.py (✅ 100% coverage)
│       ├── serializers.py (next)
│       ├── views.py (next)
│       ├── urls.py (next)
│       ├── admin.py
│       └── tests/
│           ├── factories.py (✅)
│           ├── test_models.py (✅ 25 tests)
│           ├── test_serializers.py (next)
│           └── test_api.py (next)
├── bicare360/
│   ├── settings/
│   │   ├── base.py (✅)
│   │   ├── dev.py (✅)
│   │   ├── test.py (✅)
│   │   └── prod.py (✅)
│   ├── urls.py
│   └── wsgi.py
├── requirements/
│   ├── base.txt (✅)
│   ├── dev.txt (✅)
│   ├── testing.txt (✅)
│   └── prod.txt (✅)
├── pytest.ini (✅)
├── pyproject.toml (✅)
├── conftest.py (✅)
└── manage.py
```

### Technologies
- **Framework**: Django 4.2.9 + Django REST Framework 3.14
- **Database**: PostgreSQL (with PGVector for Phase 5)
- **Testing**: pytest + pytest-django + factory-boy
- **Task Queue**: Celery + Redis (configured, ready for Phase 2)
- **API Docs**: drf-spectacular
- **Code Quality**: black, isort, flake8, mypy

### TDD Methodology Demonstrated
1. ✅ Write failing tests first
2. ✅ Implement minimal code to pass tests
3. ✅ Refactor while maintaining green tests
4. ✅ Achieve 95%+ coverage before proceeding

**Status: Phase 1 - 60% Complete** 
(Models ✅ | API ⏳ | Auth ⏳)
