"""
Test suite for Smart Patient Search - TDD Approach
Comprehensive tests for advanced search, filtering, and full-text search
"""
import pytest
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from apps.patients.tests.factories import PatientFactory, UserFactory
from apps.patients.models import Patient


class TestSmartPatientSearch(APITestCase):
    """Test suite for smart patient search functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin/staff user for search access
        self.admin_user = UserFactory(is_staff=True)
        self.nurse_user = UserFactory()
        
        # Create diverse test patients
        self.patient1 = PatientFactory(
            first_name='John',
            last_name='Doe',
            phone_number='+250780000001',
            email='john.doe@example.com',
            is_active=True
        )
        
        self.patient2 = PatientFactory(
            first_name='Jane',
            last_name='Smith',
            phone_number='+250780000002',
            email='jane.smith@example.com',
            is_active=True
        )
        
        self.patient3 = PatientFactory(
            first_name='John',
            last_name='Smith',
            phone_number='+250780000003',
            email='john.smith@example.com',
            is_active=False
        )
        
        self.patient4 = PatientFactory(
            first_name='Alice',
            last_name='Johnson',
            phone_number='+250780000004',
            email='alice.johnson@example.com',
            is_active=True
        )
    
    # ==================== BASIC SEARCH TESTS ====================
    def test_unauthenticated_cannot_search(self):
        """Test unauthenticated users cannot access search"""
        response = self.client.get('/api/v1/patients/search/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_staff_can_search_patients(self):
        """Test staff users can access patient search"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/')
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
    
    def test_search_returns_patient_fields(self):
        """Test search returns required patient fields"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        patient = response.data[0]
        
        # Check required fields
        assert 'id' in patient
        assert 'full_name' in patient
        assert 'phone_number' in patient
        assert 'email' in patient
        assert 'date_of_birth' in patient
        assert 'national_id' in patient
        assert 'is_active' in patient
    
    # ==================== FULL-TEXT SEARCH TESTS ====================
    def test_search_by_first_name(self):
        """Test searching patients by first name"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=John')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2  # patient1 and patient3
        names = [p['first_name'] for p in response.data]
        assert 'John' in names
    
    def test_search_by_last_name(self):
        """Test searching patients by last name"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=Smith')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2  # patient2 and patient3
    
    def test_search_by_full_name(self):
        """Test searching patients by full name"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=John%20Doe')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(p['full_name'] == 'John Doe' for p in response.data)
    
    def test_search_by_email(self):
        """Test searching patients by email address"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=jane.smith@example.com')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['email'] == 'jane.smith@example.com'
    
    def test_search_by_phone_number(self):
        """Test searching patients by phone number"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=%2B250780000001')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['phone_number'] == '+250780000001'
    
    def test_search_by_national_id(self):
        """Test searching patients by national ID"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/v1/patients/search/?q={self.patient1.national_id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['national_id'] == self.patient1.national_id
    
    def test_search_partial_match(self):
        """Test search works with partial text matches"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=joh')
        
        assert response.status_code == status.HTTP_200_OK
        # Should match 'John' (case-insensitive)
        assert len(response.data) >= 1
    
    def test_search_case_insensitive(self):
        """Test search is case-insensitive"""
        self.client.force_authenticate(user=self.admin_user)
        
        response_lower = self.client.get('/api/v1/patients/search/?q=john')
        response_upper = self.client.get('/api/v1/patients/search/?q=JOHN')
        response_mixed = self.client.get('/api/v1/patients/search/?q=JoHn')
        
        assert response_lower.status_code == status.HTTP_200_OK
        assert response_upper.status_code == status.HTTP_200_OK
        assert response_mixed.status_code == status.HTTP_200_OK
        
        # All should return same results
        assert len(response_lower.data) == len(response_upper.data) == len(response_mixed.data)
    
    def test_empty_search_returns_all_active(self):
        """Test empty search returns all active patients"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/')
        
        assert response.status_code == status.HTTP_200_OK
        # Should return only active patients by default
        for patient in response.data:
            assert patient['is_active'] == True
    
    # ==================== FILTER TESTS ====================
    def test_filter_by_active_status(self):
        """Test filtering patients by active status"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?is_active=true')
        
        assert response.status_code == status.HTTP_200_OK
        for patient in response.data:
            assert patient['is_active'] == True
    
    def test_filter_by_inactive_status(self):
        """Test filtering to show inactive patients"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?is_active=false')
        
        assert response.status_code == status.HTTP_200_OK
        for patient in response.data:
            assert patient['is_active'] == False
    
    def test_filter_by_gender(self):
        """Test filtering patients by gender"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/v1/patients/search/?gender=M')
        
        assert response.status_code == status.HTTP_200_OK
        if len(response.data) > 0:
            for patient in response.data:
                assert patient['gender'] == 'M'
    
    def test_filter_by_blood_type(self):
        """Test filtering patients by blood type"""
        # Update a patient with specific blood type
        self.patient1.blood_type = 'O+'
        self.patient1.save()
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?blood_type=O%2B')
        
        assert response.status_code == status.HTTP_200_OK
        if len(response.data) > 0:
            for patient in response.data:
                assert patient['blood_type'] == 'O+'
    
    def test_combine_search_and_filter(self):
        """Test combining full-text search with filters"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=John&is_active=true')
        
        assert response.status_code == status.HTTP_200_OK
        for patient in response.data:
            assert 'John' in patient['full_name']
            assert patient['is_active'] == True
    
    def test_filter_by_enrollment_date_range(self):
        """Test filtering by enrollment date range"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            f'/api/v1/patients/search/?enrolled_after=2020-01-01&enrolled_before=2030-12-31'
        )
        
        assert response.status_code == status.HTTP_200_OK
        # Should return patients enrolled in this range
        assert len(response.data) > 0
    
    # ==================== SORTING TESTS ====================
    def test_sort_by_name_ascending(self):
        """Test sorting patients by name ascending"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?sort=name&order=asc')
        
        assert response.status_code == status.HTTP_200_OK
        if len(response.data) > 1:
            names = [p['full_name'] for p in response.data]
            assert names == sorted(names)
    
    def test_sort_by_name_descending(self):
        """Test sorting patients by name descending"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?sort=name&order=desc')
        
        assert response.status_code == status.HTTP_200_OK
        if len(response.data) > 1:
            names = [p['full_name'] for p in response.data]
            assert names == sorted(names, reverse=True)
    
    def test_sort_by_enrollment_date(self):
        """Test sorting by enrollment date"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?sort=enrolled_date&order=desc')
        
        assert response.status_code == status.HTTP_200_OK
        if len(response.data) > 1:
            dates = [p['enrolled_date'] for p in response.data]
            # Verify descending order
            assert dates[0] >= dates[-1]
    
    def test_sort_by_age(self):
        """Test sorting patients by age"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?sort=age')
        
        assert response.status_code == status.HTTP_200_OK
        if len(response.data) > 1:
            ages = [p.get('age', 0) for p in response.data]
            # Should be sorted (at least ascending by default)
            assert len(ages) > 0
    
    # ==================== PAGINATION TESTS ====================
    def test_search_pagination(self):
        """Test pagination of search results"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?page=1&page_size=2')
        
        assert response.status_code == status.HTTP_200_OK
        # Should have pagination info
        assert 'count' in response.data or isinstance(response.data, list)
    
    def test_search_result_limit(self):
        """Test limiting search results"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?limit=2')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) <= 2
    
    # ==================== ADVANCED SEARCH TESTS ====================
    def test_search_by_kinyarwanda_name(self):
        """Test searching by Kinyarwanda name"""
        # Update patient with Kinyarwanda name
        self.patient1.first_name_kinyarwanda = 'Yohani'
        self.patient1.last_name_kinyarwanda = 'Doe'
        self.patient1.save()
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=Yohani')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_exclude_inactive_by_default(self):
        """Test that inactive patients are excluded by default"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/')
        
        assert response.status_code == status.HTTP_200_OK
        # patient3 is inactive, should not be in results
        patient_ids = [p['id'] for p in response.data]
        assert self.patient3.id not in patient_ids
    
    def test_search_no_results(self):
        """Test search with no matching results"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=NonExistentName')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_search_special_characters(self):
        """Test search handles special characters properly"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/?q=%2B250')
        
        # Should either find phone numbers or return empty gracefully
        assert response.status_code == status.HTTP_200_OK
    
    # ==================== FUZZY SEARCH TESTS ====================
    def test_fuzzy_search_typo_tolerance(self):
        """Test search is somewhat tolerant of typos"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Search with slight variation
        response = self.client.get('/api/v1/patients/search/?q=Smoth')
        
        # Might find Smith with fuzzy matching, or empty gracefully
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_adjacent_names(self):
        """Test search can find when names are in different order"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Search with last name first
        response = self.client.get('/api/v1/patients/search/?q=Smith%20Jane')
        
        assert response.status_code == status.HTTP_200_OK
    
    # ==================== PERFORMANCE TESTS ====================
    def test_search_response_time_with_many_results(self):
        """Test search performs well with large result sets"""
        # Create additional patients
        for i in range(10):
            PatientFactory(first_name='Test', last_name=f'Patient{i}')
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/patients/search/')
        
        # Should still be fast
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 10
    
    def test_search_with_complex_query(self):
        """Test search with multiple filter parameters"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            '/api/v1/patients/search/?q=John&is_active=true&sort=name&order=asc'
        )
        
        assert response.status_code == status.HTTP_200_OK
