# BiCare360 Testing Guide

## Overview

This guide documents the comprehensive testing strategy for BiCare360, emphasizing Test-Driven Development (TDD), deep unit testing, integration testing, and boundary testing.

---

## Testing Philosophy

### Core Principles

1. **Test-Driven Development (TDD)**
   - Write tests BEFORE implementation
   - Red → Green → Refactor cycle
   - Tests define expected behavior

2. **95% Coverage Minimum**
   - Enforced via pytest.ini configuration
   - CI/CD gate at 95%
   - HTML coverage reports for visibility

3. **Comprehensive Testing**
   - Unit tests (isolated component testing)
   - Integration tests (full stack testing)
   - Boundary tests (edge cases & limits)
   - Property-based tests (data validation)

4. **Rwanda Context-Aware**
   - National ID format (16 digits)
   - Phone numbers (+250 prefix)
   - Administrative structure (5 levels)
   - Multi-language support (Kinyarwanda/English/French)

---

## Test Types

### 1. Unit Tests

**Purpose:** Test individual components in isolation

**Location:** `test_models.py`, `test_serializers.py`

**Example:**
```python
@pytest.mark.django_db
class TestPatientModel:
    def test_patient_age_calculation(self):
        """Test age is calculated correctly from date of birth."""
        past_date = date.today() - timedelta(days=365 * 25)
        patient = PatientFactory(date_of_birth=past_date)
        assert patient.age == 25
```

**Coverage:**
- Model methods and properties
- Serializer validation logic
- Utility functions
- Business logic calculations

### 2. Integration Tests

**Purpose:** Test full request/response cycles

**Location:** `test_api.py`

**Marker:** `@pytest.mark.integration`

**Example:**
```python
@pytest.mark.django_db
@pytest.mark.integration
class TestPatientCreateAPI:
    def test_create_patient_success(self, authenticated_client):
        """Test creating a patient with valid data."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "national_id": "1234567890123456",
            "phone_number": "+250788123456",
        }
        response = authenticated_client.post("/api/v1/patients/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Patient.objects.filter(national_id="1234567890123456").exists()
```

**Coverage:**
- API endpoints (CRUD operations)
- Authentication/authorization
- Request validation
- Response formatting
- Database persistence
- Multi-model interactions

### 3. View Layer Tests

**Purpose:** Test view logic, query optimization, filtering

**Location:** `test_views.py`

**Example:**
```python
@pytest.mark.django_db
class TestPatientViewSetQueryOptimization:
    def test_list_patients_query_count(self, authenticated_client, django_assert_num_queries):
        """Test that listing patients doesn't cause N+1 queries."""
        for _ in range(5):
            patient = PatientFactory()
            AddressFactory(patient=patient)
            EmergencyContactFactory.create_batch(2, patient=patient)
        
        with django_assert_num_queries(3):  # Optimized queries
            response = authenticated_client.get("/api/v1/patients/")
            assert response.status_code == status.HTTP_200_OK
```

**Coverage:**
- Query optimization (N+1 prevention)
- Serializer class selection
- Filtering and searching
- Ordering
- Custom actions
- Error handling

### 4. Boundary & Edge Case Tests

**Purpose:** Test data limits, special cases, extreme values

**Location:** `test_edge_cases.py`

**Example:**
```python
@pytest.mark.django_db
class TestPatientBoundaryConditions:
    def test_patient_with_very_old_date_of_birth(self):
        """Test patient with very old date of birth (120 years)."""
        old_date = date.today() - timedelta(days=365 * 120)
        patient = PatientFactory(date_of_birth=old_date)
        assert patient.age >= 119
        assert patient.age <= 120
    
    def test_national_id_15_digits_fails(self):
        """Test that 15-digit national ID fails validation."""
        with pytest.raises(ValidationError):
            patient = PatientFactory.build(national_id="123456789012345")
            patient.full_clean()
    
    def test_patient_with_emoji_in_name(self):
        """Test that emoji in name is stored."""
        patient = PatientFactory(first_name="John😊")
        assert "😊" in patient.first_name
```

**Coverage:**
- Data validation boundaries (min/max lengths)
- Format validation (phone, email, ID)
- Unicode & special characters
- Extreme values (ages, coordinates)
- Concurrency scenarios
- Race conditions

---

## Test Organization

### File Structure

```
apps/patients/tests/
├── __init__.py
├── factories.py              # Test data factories
├── test_models.py            # Unit tests for models
├── test_serializers.py       # Unit tests for serializers
├── test_views.py             # View logic & optimization tests
├── test_api.py               # Integration tests (full stack)
└── test_edge_cases.py        # Boundary & edge case tests
```

### Naming Conventions

**Test Classes:**
- `Test<ComponentName>`: e.g., `TestPatientModel`, `TestPatientListAPI`
- Organize related tests together

**Test Methods:**
- `test_<action>_<scenario>`: e.g., `test_create_patient_with_invalid_phone_number`
- Descriptive, explains what is being tested
- Use present tense

**Docstrings:**
- Every test has a docstring explaining its purpose
- Focus on "why" not "what"

**Examples:**
```python
class TestPatientModel:
    def test_patient_national_id_must_be_unique(self):
        """Test that two patients cannot have the same national ID."""
        # Test implementation
```

---

## Testing Infrastructure

### Configuration Files

#### pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = bicare360.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = 
    --reuse-db
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=95
    -p no:asyncio
```

#### conftest.py
```python
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    """Return unauthenticated API client."""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    """Return authenticated API client."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    api_client.force_authenticate(user=user)
    return api_client
```

### Factory Pattern

**Purpose:** Generate realistic, consistent test data

**Location:** `factories.py`

**Example:**
```python
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.patients.models import Patient, Address

fake = Faker()

class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient
    
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=0, maximum_age=100)
    gender = factory.Faker("random_element", elements=["M", "F", "O"])
    national_id = factory.LazyFunction(lambda: fake.numerify(text="################"))
    phone_number = factory.LazyFunction(lambda: f"+250{fake.numerify(text='#########')}")
    email = factory.Faker("email")
    language_preference = "kin"
    prefers_sms = True
    enrolled_by = factory.SubFactory(UserFactory)

class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address
    
    patient = factory.SubFactory(PatientFactory)
    province = factory.Faker("random_element", elements=["Kigali", "Eastern", "Northern", "Southern", "Western"])
    district = "Gasabo"
    sector = "Kimironko"
    cell = "Biryogo"
    village = "Umuganda"
    street_address = factory.Faker("street_address")
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
```

**Usage:**
```python
# Create single instance
patient = PatientFactory()

# Create with specific attributes
patient = PatientFactory(gender="F", email="specific@email.com")

# Create multiple instances
patients = PatientFactory.create_batch(10)

# Create without saving (for validation tests)
patient = PatientFactory.build(national_id="invalid")
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest apps/patients/tests/

# Run with verbose output
pytest apps/patients/tests/ -v

# Run specific test file
pytest apps/patients/tests/test_models.py

# Run specific test class
pytest apps/patients/tests/test_models.py::TestPatientModel

# Run specific test method
pytest apps/patients/tests/test_models.py::TestPatientModel::test_patient_age_calculation

# Run tests matching pattern
pytest apps/patients/tests/ -k "national_id"

# Run integration tests only
pytest apps/patients/tests/ -m integration

# Run with coverage
pytest apps/patients/tests/ --cov=apps/patients --cov-report=html

# Run failed tests only
pytest apps/patients/tests/ --lf

# Run in parallel (faster)
pytest apps/patients/tests/ -n auto
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest apps/patients/tests/ --cov=apps/patients --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal coverage report
pytest apps/patients/tests/ --cov=apps/patients --cov-report=term-missing

# Fail if coverage below 95%
pytest apps/patients/tests/ --cov=apps/patients --cov-fail-under=95
```

---

## Writing Effective Tests

### Best Practices

#### 1. Test One Thing
```python
# ❌ BAD - Testing multiple things
def test_patient_creation():
    patient = PatientFactory()
    assert patient.age > 0
    assert patient.full_name
    assert patient.is_active

# ✅ GOOD - Single responsibility
def test_patient_age_calculation():
    patient = PatientFactory(date_of_birth=date(2000, 1, 1))
    assert patient.age == 24

def test_patient_full_name_property():
    patient = PatientFactory(first_name="John", last_name="Doe")
    assert patient.full_name == "John Doe"
```

#### 2. Use Descriptive Names
```python
# ❌ BAD
def test_patient_1():
    ...

# ✅ GOOD
def test_patient_national_id_must_be_16_digits():
    ...
```

#### 3. Arrange-Act-Assert Pattern
```python
def test_create_patient_with_address(authenticated_client):
    # Arrange - Set up test data
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "national_id": "1234567890123456",
        # ... other fields
    }
    
    # Act - Perform the action
    response = authenticated_client.post("/api/v1/patients/", data, format="json")
    
    # Assert - Verify the outcome
    assert response.status_code == status.HTTP_201_CREATED
    assert Patient.objects.filter(national_id="1234567890123456").exists()
```

#### 4. Test Error Cases
```python
def test_create_patient_with_invalid_phone_number(authenticated_client):
    """Test that invalid phone number format is rejected."""
    data = {
        # ... valid fields ...
        "phone_number": "invalid",  # Missing +250 prefix
    }
    response = authenticated_client.post("/api/v1/patients/", data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "phone_number" in response.data
```

#### 5. Use Fixtures for Setup
```python
@pytest.fixture
def patient_with_address():
    """Create a patient with an address."""
    patient = PatientFactory()
    AddressFactory(patient=patient)
    return patient

def test_patient_has_address(patient_with_address):
    assert hasattr(patient_with_address, 'address')
    assert patient_with_address.address is not None
```

#### 6. Test Database Constraints
```python
def test_patient_national_id_must_be_unique():
    """Test that two patients cannot have the same national ID."""
    PatientFactory(national_id="1234567890123456")
    
    with pytest.raises(IntegrityError):
        PatientFactory(national_id="1234567890123456")
```

#### 7. Test Property-Based Logic
```python
def test_patient_with_leap_year_birthday():
    """Test patient born on Feb 29 (leap year)."""
    patient = PatientFactory(date_of_birth=date(2000, 2, 29))
    assert patient.date_of_birth.month == 2
    assert patient.date_of_birth.day == 29
```

---

## Common Patterns

### Testing Validation

```python
def test_field_validation_fails(self):
    """Test that invalid data raises ValidationError."""
    with pytest.raises(ValidationError):
        obj = ModelFactory.build(field="invalid_value")
        obj.full_clean()
```

### Testing Relationships

```python
def test_cascade_delete(self):
    """Test that child is deleted when parent is deleted."""
    parent = ParentFactory()
    child = ChildFactory(parent=parent)
    
    parent.delete()
    
    assert not Child.objects.filter(pk=child.pk).exists()
```

### Testing API Endpoints

```python
def test_list_endpoint(self, authenticated_client):
    """Test listing resources."""
    ModelFactory.create_batch(5)
    
    response = authenticated_client.get("/api/v1/resource/")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 5
```

### Testing Query Optimization

```python
def test_no_n_plus_1_queries(self, authenticated_client, django_assert_num_queries):
    """Test that endpoint uses optimized queries."""
    ModelFactory.create_batch(10)
    
    with django_assert_num_queries(3):  # Adjust expected count
        response = authenticated_client.get("/api/v1/resource/")
        assert response.status_code == status.HTTP_200_OK
```

---

## Debugging Tests

### Failed Test Analysis

```bash
# Show detailed output
pytest apps/patients/tests/test_models.py::test_failing -vv

# Show local variables on failure
pytest apps/patients/tests/test_models.py::test_failing -l

# Drop into debugger on failure
pytest apps/patients/tests/test_models.py::test_failing --pdb

# Show print statements
pytest apps/patients/tests/test_models.py::test_failing -s
```

### Using pytest Debugger

```python
def test_something():
    patient = PatientFactory()
    
    import pytest; pytest.set_trace()  # Debugger breakpoint
    
    assert patient.age > 0
```

---

## Continuous Integration

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        args: [apps/patients/tests/, --cov=apps/patients, --cov-fail-under=95]
        language: system
        pass_filenames: false
        always_run: true
```

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: |
          pip install -r requirements/testing.txt
      - name: Run tests
        run: |
          pytest apps/patients/tests/ --cov=apps/patients --cov-fail-under=95
```

---

## Coverage Analysis

### Identifying Uncovered Code

```bash
# Generate coverage report
pytest apps/patients/tests/ --cov=apps/patients --cov-report=term-missing

# View missing lines
Name                           Stmts   Miss Branch BrPart   Cover   Missing
---------------------------------------------------------------------------
apps/patients/serializers.py      74      5     20      3  89.36%   162, 167-169, 204
```

### Addressing Coverage Gaps

1. **Identify missing lines** in coverage report
2. **Analyze why code is uncovered:**
   - Dead code? Remove it
   - Error handling? Write error test
   - Edge case? Add boundary test
3. **Write targeted test** for uncovered code
4. **Verify coverage improvement**

---

## Performance Testing

### Query Count Testing

```python
def test_list_endpoint_query_count(authenticated_client, django_assert_num_queries):
    """Test that list endpoint uses minimal queries."""
    ModelFactory.create_batch(100)
    
    with django_assert_num_queries(3):  # Should not increase with data size
        response = authenticated_client.get("/api/v1/resource/")
        assert response.status_code == status.HTTP_200_OK
```

### Response Time Testing

```python
import time

def test_list_endpoint_performance(authenticated_client):
    """Test that list endpoint responds quickly."""
    ModelFactory.create_batch(100)
    
    start = time.time()
    response = authenticated_client.get("/api/v1/resource/")
    duration = time.time() - start
    
    assert response.status_code == status.HTTP_200_OK
    assert duration < 0.5  # Should respond within 500ms
```

---

## Conclusion

This testing guide provides comprehensive strategies for ensuring BiCare360 meets the highest quality standards. By following TDD principles, maintaining 95%+ coverage, and implementing deep unit, integration, and boundary tests, we ensure a robust, reliable healthcare platform for Rwanda.

**Key Takeaways:**
- ✅ Write tests BEFORE implementation (TDD)
- ✅ Aim for 95%+ coverage on all modules
- ✅ Test units, integration, boundaries, and edge cases
- ✅ Use factories for consistent test data
- ✅ Follow naming conventions and best practices
- ✅ Run tests frequently during development
- ✅ Analyze and address coverage gaps
- ✅ Optimize queries and performance

**Status:** This guide serves as the testing blueprint for all BiCare360 modules.
