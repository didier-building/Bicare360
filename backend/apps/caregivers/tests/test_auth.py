"""
Tests for Caregiver Authentication and Portal functionality.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.caregivers.models import Caregiver, CaregiverBooking
from apps.patients.models import Patient

User = get_user_model()


@pytest.mark.django_db
class TestCaregiverLogin:
    """Tests for caregiver login endpoint."""
    
    def setup_method(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a test user and caregiver profile
        self.user = User.objects.create_user(
            username='testcaregiver',
            email='caregiver@test.com',
            password='testpass123'
        )
        
        self.caregiver = Caregiver.objects.create(
            user=self.user,
            first_name='Jane',
            last_name='Doe',
            email='caregiver@test.com',
            phone_number='+250788123456',
            profession='registered_nurse',
            experience_years=5,
            bio='Test caregiver bio',
            province='Kigali',
            district='Gasabo',
            hourly_rate=50.00,
            is_verified=True,
            is_active=True
        )
    
    def test_successful_login(self):
        """Test successful caregiver login."""
        response = self.client.post('/api/v1/caregivers/login/', {
            'email': 'caregiver@test.com',
            'password': 'testpass123'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'caregiver' in response.data
        assert 'user' in response.data
        assert response.data['caregiver']['email'] == 'caregiver@test.com'
        assert response.data['user']['role'] == 'caregiver'
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
    
    def test_login_with_invalid_email(self):
        """Test login with non-existent email."""
        response = self.client.post('/api/v1/caregivers/login/', {
            'email': 'nonexistent@test.com',
            'password': 'testpass123'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
    
    def test_login_with_wrong_password(self):
        """Test login with incorrect password."""
        response = self.client.post('/api/v1/caregivers/login/', {
            'email': 'caregiver@test.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
    
    def test_login_missing_email(self):
        """Test login without email."""
        response = self.client.post('/api/v1/caregivers/login/', {
            'password': 'testpass123'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_login_missing_password(self):
        """Test login without password."""
        response = self.client.post('/api/v1/caregivers/login/', {
            'email': 'caregiver@test.com'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_login_inactive_caregiver(self):
        """Test login with inactive caregiver account."""
        self.caregiver.is_active = False
        self.caregiver.save()
        
        response = self.client.post('/api/v1/caregivers/login/', {
            'email': 'caregiver@test.com',
            'password': 'testpass123'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
    
    def test_login_caregiver_without_user(self):
        """Test login for caregiver profile without linked user."""
        # Create caregiver without user
        caregiver_no_user = Caregiver.objects.create(
            first_name='John',
            last_name='Smith',
            email='nouser@test.com',
            phone_number='+250788654321',
            profession='home_health_aide',
            experience_years=3,
            province='Kigali',
            district='Kicukiro',
            hourly_rate=30.00
        )
        
        response = self.client.post('/api/v1/caregivers/login/', {
            'email': 'nouser@test.com',
            'password': 'testpass123'
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data


@pytest.mark.django_db
class TestCaregiverDashboardStats:
    """Tests for caregiver dashboard stats endpoint."""
    
    def setup_method(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create caregiver user
        self.user = User.objects.create_user(
            username='testcaregiver',
            email='caregiver@test.com',
            password='testpass123'
        )
        
        self.caregiver = Caregiver.objects.create(
            user=self.user,
            first_name='Jane',
            last_name='Doe',
            email='caregiver@test.com',
            phone_number='+250788123456',
            profession='registered_nurse',
            experience_years=5,
            bio='Test caregiver bio',
            province='Kigali',
            district='Gasabo',
            hourly_rate=50.00,
            rating=4.5,
            total_reviews=10,
            is_verified=True,
            is_active=True
        )
        
        # Create patient for bookings
        self.patient_user = User.objects.create_user(
            username='testpatient',
            email='patient@test.com',
            password='testpass123'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            first_name='John',
            last_name='Patient',
            email='patient@test.com',
            phone_number='+250788999999',
            national_id='1234567890123456',
            date_of_birth='1990-01-01',
            gender='M'
        )
    
    def test_get_dashboard_stats_authenticated(self):
        """Test getting dashboard stats for authenticated caregiver."""
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/v1/caregivers/dashboard-stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_bookings' in response.data
        assert 'pending_bookings' in response.data
        assert 'confirmed_bookings' in response.data
        assert 'upcoming_bookings' in response.data
        assert 'completed_bookings' in response.data
        assert 'total_earnings' in response.data
        assert 'rating' in response.data
        assert response.data['rating'] == 4.5
    
    def test_get_dashboard_stats_unauthenticated(self):
        """Test getting dashboard stats without authentication."""
        response = self.client.get('/api/v1/caregivers/dashboard-stats/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_dashboard_stats_with_bookings(self):
        """Test dashboard stats calculation with actual bookings."""
        # Create some bookings
        from datetime import datetime, timedelta
        from django.utils import timezone as tz
        
        now = tz.now()
        
        # Pending booking
        CaregiverBooking.objects.create(
            patient=self.patient,
            caregiver=self.caregiver,
            service_type='Home Care',
            start_datetime=now + timedelta(days=1),
            end_datetime=now + timedelta(days=1, hours=4),
            duration_hours=4,
            hourly_rate=50.00,
            total_cost=200.00,
            status='pending'
        )
        
        # Confirmed booking
        CaregiverBooking.objects.create(
            patient=self.patient,
            caregiver=self.caregiver,
            service_type='Nursing Care',
            start_datetime=now + timedelta(days=2),
            end_datetime=now + timedelta(days=2, hours=3),
            duration_hours=3,
            hourly_rate=50.00,
            total_cost=150.00,
            status='confirmed'
        )
        
        # Completed booking
        CaregiverBooking.objects.create(
            patient=self.patient,
            caregiver=self.caregiver,
            service_type='Personal Care',
            start_datetime=now - timedelta(days=1),
            end_datetime=now - timedelta(days=1) + timedelta(hours=5),
            duration_hours=5,
            hourly_rate=50.00,
            total_cost=250.00,
            status='completed'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/caregivers/dashboard-stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_bookings'] == 3
        assert response.data['pending_bookings'] == 1
        assert response.data['confirmed_bookings'] == 1
        assert response.data['completed_bookings'] == 1
        assert response.data['upcoming_bookings'] == 2
        assert 'upcoming_bookings_list' in response.data
        assert len(response.data['upcoming_bookings_list']) == 2
    
    def test_dashboard_stats_no_caregiver_profile(self):
        """Test dashboard stats for user without caregiver profile."""
        # Create user without caregiver profile
        user_no_profile = User.objects.create_user(
            username='nocaregiver',
            email='nocaregiver@test.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=user_no_profile)
        response = self.client.get('/api/v1/caregivers/dashboard-stats/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data


@pytest.mark.django_db
class TestCaregiverSerializers:
    """Tests for caregiver serializers."""
    
    def test_caregiver_auth_serializer(self):
        """Test CaregiverAuthSerializer includes correct fields."""
        from apps.caregivers.serializers import CaregiverAuthSerializer
        
        user = User.objects.create_user(
            username='testcaregiver',
            email='caregiver@test.com',
            password='testpass123'
        )
        
        caregiver = Caregiver.objects.create(
            user=user,
            first_name='Jane',
            last_name='Doe',
            email='caregiver@test.com',
            phone_number='+250788123456',
            profession='registered_nurse',
            experience_years=5,
            bio='Test bio',
            province='Kigali',
            district='Gasabo',
            hourly_rate=50.00,
            rating=4.7,
            total_reviews=15
        )
        
        serializer = CaregiverAuthSerializer(caregiver)
        data = serializer.data
        
        assert 'id' in data
        assert 'full_name' in data
        assert data['full_name'] == 'Jane Doe'
        assert data['email'] == 'caregiver@test.com'
        assert data['profession'] == 'registered_nurse'
        assert data['rating'] == '4.70'
        assert data['total_reviews'] == 15
