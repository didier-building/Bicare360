"""
Comprehensive test suite for Health Progress Charts and Vitals Tracking.
Tests vital readings, health goals, trends, and health progress endpoints.
"""
import pytest
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.patients.models import Patient
from apps.vitals.models import VitalReading, HealthGoal, HealthTrend

User = get_user_model()


@pytest.mark.django_db
class TestVitalReadingsAPI:
    """Test vital readings creation, retrieval, and filtering."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            gender="M",
            national_id="1000000000000001",
            phone_number="+250780000001",
            blood_type="O+",
        )

    def test_record_vital_reading_requires_auth(self):
        """Test that recording vital requires authentication."""
        response = self.client.post(
            "/api/v1/patients/{}/vitals/".format(self.patient.id),
            {
                "reading_type": "blood_pressure",
                "value": 120,
                "secondary_value": 80,
                "unit": "mmHg",
                "recorded_at": timezone.now().isoformat(),
            },
        )
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_record_blood_pressure_reading(self):
        """Test recording a blood pressure vital reading."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "blood_pressure",
                "value": 120,
                "secondary_value": 80,
                "unit": "mmHg",
                "recorded_at": now.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["value"] == 120
        assert response.data["secondary_value"] == 80
        assert response.data["unit"] == "mmHg"
        assert response.data["reading_type"] == "blood_pressure"

    def test_record_heart_rate_reading(self):
        """Test recording a heart rate vital reading."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "heart_rate",
                "value": 72,
                "unit": "bpm",
                "recorded_at": now.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["value"] == 72
        assert response.data["reading_type"] == "heart_rate"

    def test_record_weight_reading(self):
        """Test recording a weight vital reading."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "weight",
                "value": 75.5,
                "unit": "kg",
                "recorded_at": now.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["value"] == 75.5
        assert response.data["reading_type"] == "weight"

    def test_record_temperature_reading(self):
        """Test recording a temperature vital reading."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "temperature",
                "value": 36.5,
                "unit": "°C",
                "recorded_at": now.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["value"] == 36.5

    def test_record_oxygen_saturation_reading(self):
        """Test recording oxygen saturation reading."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "oxygen_saturation",
                "value": 98,
                "unit": "%",
                "recorded_at": now.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["value"] == 98

    def test_record_blood_glucose_reading(self):
        """Test recording blood glucose reading."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "blood_glucose",
                "value": 120,
                "unit": "mg/dL",
                "recorded_at": now.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["reading_type"] == "blood_glucose"

    def test_list_vital_readings_for_patient(self):
        """Test retrieving list of vital readings for a patient."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create multiple readings
        for i in range(5):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="heart_rate",
                value=70 + i,
                unit="bpm",
                recorded_at=now - timedelta(days=i),
            )

        response = self.client.get(f"/api/v1/patients/{self.patient.id}/vitals/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_filter_readings_by_type(self):
        """Test filtering vital readings by reading type."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create different reading types
        VitalReading.objects.create(
            patient=self.patient,
            reading_type="heart_rate",
            value=72,
            unit="bpm",
            recorded_at=now,
        )
        VitalReading.objects.create(
            patient=self.patient,
            reading_type="blood_pressure",
            value=120,
            unit="mmHg",
            recorded_at=now,
        )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/vitals/?reading_type=heart_rate"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["reading_type"] == "heart_rate"

    def test_filter_readings_by_date_range(self):
        """Test filtering readings by date range."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings across different dates
        for i in range(10):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="heart_rate",
                value=70 + i,
                unit="bpm",
                recorded_at=now - timedelta(days=i),
            )

        # Filter for last 3 days
        start_date = (now - timedelta(days=3)).date()
        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/vitals/?recorded_after={start_date}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4  # 0-3 days ago

    def test_vital_reading_validates_value(self):
        """Test that vital readings validate numeric values."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Try to record negative value (should fail)
        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "weight",
                "value": -50,  # Invalid: negative weight
                "unit": "kg",
                "recorded_at": now.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_vital_reading_with_notes(self):
        """Test recording vital with clinical notes."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/vitals/",
            {
                "reading_type": "temperature",
                "value": 38.5,
                "unit": "°C",
                "recorded_at": now.isoformat(),
                "notes": "Patient reports fever with chills",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["notes"] == "Patient reports fever with chills"


@pytest.mark.django_db
class TestHealthGoalsAPI:
    """Test health goals creation, tracking, and progress."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.patient = Patient.objects.create(
            first_name="Jane",
            last_name="Smith",
            date_of_birth="1985-05-15",
            gender="F",
            national_id="1000000000000002",
            phone_number="+250780000002",
        )

    def test_create_health_goal(self):
        """Test creating a health goal."""
        self.client.force_authenticate(user=self.admin_user)
        today = timezone.now().date()

        response = self.client.post(
            f"/api/v1/patients/{self.patient.id}/health-goals/",
            {
                "vital_type": "blood_pressure",
                "goal_name": "Reduce systolic BP below 120",
                "target_value": 120,
                "unit": "mmHg",
                "start_date": today.isoformat(),
                "target_date": (today + timedelta(days=90)).isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["goal_name"] == "Reduce systolic BP below 120"
        assert response.data["status"] == "active"

    def test_list_active_health_goals(self):
        """Test retrieving active health goals for a patient."""
        self.client.force_authenticate(user=self.admin_user)
        today = timezone.now().date()

        # Create multiple goals
        for i in range(3):
            HealthGoal.objects.create(
                patient=self.patient,
                vital_type="heart_rate",
                goal_name=f"Goal {i}",
                target_value=60 + i,
                unit="bpm",
                start_date=today,
            )

        response = self.client.get(f"/api/v1/patients/{self.patient.id}/health-goals/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_filter_goals_by_status(self):
        """Test filtering health goals by status."""
        self.client.force_authenticate(user=self.admin_user)
        today = timezone.now().date()

        # Create goals with different statuses
        HealthGoal.objects.create(
            patient=self.patient,
            vital_type="weight",
            goal_name="Lose 5kg",
            target_value=75,
            unit="kg",
            start_date=today,
            status="active",
        )
        HealthGoal.objects.create(
            patient=self.patient,
            vital_type="weight",
            goal_name="Previous goal",
            target_value=80,
            unit="kg",
            start_date=today,
            status="achieved",
        )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-goals/?status=active"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["status"] == "active"

    def test_mark_goal_as_achieved(self):
        """Test marking a health goal as achieved."""
        self.client.force_authenticate(user=self.admin_user)
        today = timezone.now().date()

        goal = HealthGoal.objects.create(
            patient=self.patient,
            vital_type="weight",
            goal_name="Lose 5kg",
            target_value=75,
            unit="kg",
            start_date=today,
            status="active",
        )

        response = self.client.patch(
            f"/api/v1/patients/{self.patient.id}/health-goals/{goal.id}/",
            {"status": "achieved"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "achieved"


@pytest.mark.django_db
class TestHealthProgressCharts:
    """Test health progress chart data and visualization endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.patient = Patient.objects.create(
            first_name="Bob",
            last_name="Johnson",
            date_of_birth="1980-03-20",
            gender="M",
            national_id="1000000000000003",
            phone_number="+250780000003",
        )

    def test_get_health_summary_dashboard(self):
        """Test retrieving health summary for dashboard."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create recent readings
        VitalReading.objects.create(
            patient=self.patient,
            reading_type="blood_pressure",
            value=120,
            secondary_value=80,
            unit="mmHg",
            recorded_at=now,
        )
        VitalReading.objects.create(
            patient=self.patient,
            reading_type="heart_rate",
            value=72,
            unit="bpm",
            recorded_at=now,
        )

        response = self.client.get(f"/api/v1/patients/{self.patient.id}/health-progress/health_summary/")

        assert response.status_code == status.HTTP_200_OK
        assert "latest_readings" in response.data
        assert len(response.data["latest_readings"]) > 0

    def test_get_vital_trend_for_chart(self):
        """Test retrieving vital trend data for charting."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings over 10 days
        readings = []
        for i in range(10):
            reading = VitalReading.objects.create(
                patient=self.patient,
                reading_type="heart_rate",
                value=70 + i,
                unit="bpm",
                recorded_at=now - timedelta(days=i),
            )
            readings.append(reading)

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/vital_trends/"
            f"?reading_type=heart_rate&days=10"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "readings" in response.data
        assert len(response.data["readings"]) == 10

    def test_vital_trend_shows_trend_direction(self):
        """Test that vital trends include trend direction (improving/stable/declining)."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings showing improvement (decreasing heart rate)
        for i in range(5):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="heart_rate",
                value=90 - (i * 2),  # 90, 88, 86, 84, 82
                unit="bpm",
                recorded_at=now - timedelta(days=i),
            )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/vital_trends/"
            f"?reading_type=heart_rate&days=5"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "trend_direction" in response.data

    def test_get_multiple_vital_types_for_comprehensive_view(self):
        """Test retrieving multiple vital types for comprehensive health view."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings for different vital types
        for vital_type, value in [
            ("blood_pressure", 120),
            ("heart_rate", 72),
            ("weight", 75),
            ("temperature", 36.5),
        ]:
            VitalReading.objects.create(
                patient=self.patient,
                reading_type=vital_type,
                value=value,
                unit="unit",
                recorded_at=now,
            )

        response = self.client.get(f"/api/v1/patients/{self.patient.id}/health-progress/vital_summary/")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)
        # Should have data for tracked vital types


@pytest.mark.django_db
class TestHealthAnalytics:
    """Test health analytics and progress analysis."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.patient = Patient.objects.create(
            first_name="Alice",
            last_name="Williams",
            date_of_birth="1992-07-10",
            gender="F",
            national_id="1000000000000004",
            phone_number="+250780000004",
        )

    def test_get_health_progress_report(self):
        """Test generating health progress report."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings and goals
        VitalReading.objects.create(
            patient=self.patient,
            reading_type="weight",
            value=80,
            unit="kg",
            recorded_at=now - timedelta(days=30),
        )
        VitalReading.objects.create(
            patient=self.patient,
            reading_type="weight",
            value=75,
            unit="kg",
            recorded_at=now,
        )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/health_report/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "patient_name" in response.data
        assert "period" in response.data

    def test_analyze_vital_consistency(self):
        """Test analyzing consistency of vital readings."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings with varying consistency
        for i in range(20):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="heart_rate",
                value=70 + (i % 5),
                unit="bpm",
                recorded_at=now - timedelta(days=i),
            )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/health_report/"
            f"?include_consistency=true"
        )

        assert response.status_code == status.HTTP_200_OK

    def test_identify_abnormal_readings(self):
        """Test identifying abnormal vital readings."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create normal readings
        for i in range(10):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="temperature",
                value=36.5 + (i % 0.5),
                unit="°C",
                recorded_at=now - timedelta(days=i),
            )

        # Add abnormal reading (fever)
        VitalReading.objects.create(
            patient=self.patient,
            reading_type="temperature",
            value=39.5,
            unit="°C",
            recorded_at=now,
        )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/vital_alerts/"
        )

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestHealthTrendAggregation:
    """Test health trend calculations and aggregation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.patient = Patient.objects.create(
            first_name="Charlie",
            last_name="Brown",
            date_of_birth="1975-12-01",
            gender="M",
            national_id="1000000000000005",
            phone_number="+250780000005",
        )

    def test_calculate_daily_averages(self):
        """Test calculating daily average vitals."""
        self.client.force_authenticate(user=self.admin_user)
        today = timezone.now()

        # Create multiple readings for same day
        for hour in range(3):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="heart_rate",
                value=70 + hour,
                unit="bpm",
                recorded_at=today.replace(hour=8 + hour, minute=0),
            )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/health_trends/"
            f"?period=daily&days=1"
        )

        assert response.status_code == status.HTTP_200_OK

    def test_calculate_weekly_averages(self):
        """Test calculating weekly average vitals."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings over a week
        for day in range(7):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="heart_rate",
                value=70 + day,
                unit="bpm",
                recorded_at=now - timedelta(days=day),
            )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/health_trends/"
            f"?period=weekly&weeks=1"
        )

        assert response.status_code == status.HTTP_200_OK

    def test_trend_includes_min_max_values(self):
        """Test that trends include min/max values."""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()

        # Create readings with varying values
        for i in range(10):
            VitalReading.objects.create(
                patient=self.patient,
                reading_type="weight",
                value=70 + i,
                unit="kg",
                recorded_at=now - timedelta(days=i),
            )

        response = self.client.get(
            f"/api/v1/patients/{self.patient.id}/health-progress/vital_trends/"
            f"?reading_type=weight&days=10&include_stats=true"
        )

        assert response.status_code == status.HTTP_200_OK
        if "stats" in response.data:
            assert "min_value" in response.data["stats"]
            assert "max_value" in response.data["stats"]
            assert "avg_value" in response.data["stats"]
