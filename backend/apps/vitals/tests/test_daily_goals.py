"""
Tests for Daily Goals API (Phase 1B - Daily Goals System).

Following TDD approach: Tests written first, then implementation.
"""
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, time
from rest_framework import status
from rest_framework.test import APIClient

from apps.patients.models import Patient
from apps.vitals.models import DailyGoal, GoalProgress

User = get_user_model()


@pytest.mark.django_db
class TestDailyGoalModel:
    """Test DailyGoal model methods."""

    @pytest.fixture
    def patient(self):
        """Create a test patient."""
        user = User.objects.create_user(
            username="patient@test.com",
            email="patient@test.com",
            password="test123",
        )
        return Patient.objects.create(
            user=user,
            date_of_birth="1990-01-01",
            blood_type="O+",
        )

    @pytest.fixture
    def daily_goal(self, patient):
        """Create a test daily goal."""
        return DailyGoal.objects.create(
            patient=patient,
            title="Drink 8 glasses of water",
            category="hydration",
            target_value=8,
            recurrence_days=[0, 1, 2, 3, 4, 5, 6],  # All days
        )

    def test_create_daily_goal(self, patient):
        """Test creating a daily goal."""
        goal = DailyGoal.objects.create(
            patient=patient,
            title="Exercise 30 minutes",
            category="exercise",
            target_value=30,
            recurrence_days=[1, 3, 5],  # Mon, Wed, Fri
        )
        assert goal.id is not None
        assert goal.title == "Exercise 30 minutes"
        assert goal.current_value == 0
        assert goal.is_completed is False

    def test_tick_goal(self, daily_goal):
        """Test marking goal as complete."""
        assert daily_goal.is_completed is False
        assert daily_goal.completed_at is None
        
        daily_goal.tick()
        
        assert daily_goal.is_completed is True
        assert daily_goal.completed_at is not None
        assert daily_goal.current_value == daily_goal.target_value

    def test_untick_goal(self, daily_goal):
        """Test marking goal as incomplete."""
        daily_goal.tick()
        assert daily_goal.is_completed is True
        
        daily_goal.untick()
        
        assert daily_goal.is_completed is False
        assert daily_goal.completed_at is None

    def test_increment_goal(self, daily_goal):
        """Test incrementing goal progress."""
        assert daily_goal.current_value == 0
        
        daily_goal.increment(3)
        assert daily_goal.current_value == 3
        assert daily_goal.is_completed is False
        
        daily_goal.increment(5)
        assert daily_goal.current_value == 8
        assert daily_goal.is_completed is True  # Auto-complete when target reached

    def test_get_today_goals(self, patient):
        """Test retrieving today's active goals."""
        today_weekday = timezone.now().weekday()
        
        # Create goal for today
        goal_today = DailyGoal.objects.create(
            patient=patient,
            title="Today's goal",
            category="exercise",
            target_value=30,
            recurrence_days=[today_weekday],
        )
        
        # Create goal for different day
        other_day = (today_weekday + 1) % 7
        goal_other = DailyGoal.objects.create(
            patient=patient,
            title="Other day goal",
            category="meditation",
            target_value=10,
            recurrence_days=[other_day],
        )
        
        today_goals = DailyGoal.get_today_goals(patient)
        
        assert goal_today in today_goals
        assert goal_other not in today_goals


@pytest.mark.django_db
class TestGoalProgressModel:
    """Test GoalProgress model and streak calculation."""

    @pytest.fixture
    def patient(self):
        user = User.objects.create_user(
            username="patient2@test.com",
            email="patient2@test.com",
            password="test123",
        )
        return Patient.objects.create(
            user=user,
            date_of_birth="1990-01-01",
            blood_type="A+",
        )

    @pytest.fixture
    def goal(self, patient):
        return DailyGoal.objects.create(
            patient=patient,
            title="Morning meditation",
            category="meditation",
            target_value=15,
            recurrence_days=[0, 1, 2, 3, 4, 5, 6],
        )

    def test_create_progress_record(self, goal):
        """Test creating a progress record."""
        today = timezone.now().date()
        progress = GoalProgress.objects.create(
            goal=goal,
            date=today,
            completed=True,
            actual_value=15,
        )
        
        assert progress.id is not None
        assert progress.completed is True
        assert progress.date == today

    def test_calculate_streak_no_records(self, goal):
        """Test streak calculation with no progress records."""
        streak = GoalProgress.calculate_streak(goal)
        assert streak == 0

    def test_calculate_streak_consecutive_days(self, goal):
        """Test streak calculation with consecutive completed days."""
        today = timezone.now().date()
        
        # Create 5 consecutive days of completion
        for i in range(5):
            date = today - timedelta(days=i)
            GoalProgress.objects.create(
                goal=goal,
                date=date,
                completed=True,
                actual_value=15,
            )
        
        streak = GoalProgress.calculate_streak(goal)
        assert streak == 5

    def test_calculate_streak_broken(self, goal):
        """Test streak calculation with broken streak."""
        today = timezone.now().date()
        
        # Day 0 (today): completed
        GoalProgress.objects.create(goal=goal, date=today, completed=True, actual_value=15)
        
        # Day -1: completed
        GoalProgress.objects.create(goal=goal, date=today - timedelta(days=1), completed=True, actual_value=15)
        
        # Day -2: NOT completed (breaks streak)
        GoalProgress.objects.create(goal=goal, date=today - timedelta(days=2), completed=False, actual_value=5)
        
        # Day -3: completed (doesn't count, streak broken)
        GoalProgress.objects.create(goal=goal, date=today - timedelta(days=3), completed=True, actual_value=15)
        
        streak = GoalProgress.calculate_streak(goal)
        assert streak == 2  # Only today and yesterday

    def test_get_completion_rate(self, goal):
        """Test completion rate calculation."""
        today = timezone.now().date()
        
        # Create 7 days: 5 completed, 2 not completed
        for i in range(7):
            date = today - timedelta(days=i)
            completed = i < 5  # First 5 are completed
            GoalProgress.objects.create (
                goal=goal,
                date=date,
                completed=completed,
                actual_value=15 if completed else 5,
            )
        
        completion_rate = GoalProgress.get_completion_rate(goal, days=7)
        assert completion_rate == 71.4  # 5/7 = 71.4%

    def test_get_completion_rate_no_records(self, goal):
        """Test completion rate with no records."""
        completion_rate = GoalProgress.get_completion_rate(goal, days=7)
        assert completion_rate == 0.0


@pytest.mark.django_db
class TestDailyGoalAPI:
    """Test Daily Goals REST API endpoints."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def patient_user(self):
        return User.objects.create_user(
            username="apipatient@test.com",
            email="apipatient@test.com",
            password="test123",
        )

    @pytest.fixture
    def patient(self, patient_user):
        return Patient.objects.create(
            user=patient_user,
            date_of_birth="1990-01-01",
            blood_type="B+",
        )

    @pytest.fixture
    def authenticated_client(self, api_client, patient_user):
        """Return an authenticated API client."""
        api_client.force_authenticate(user=patient_user)
        return api_client

    def test_list_daily_goals(self, authenticated_client, patient):
        """Test listing patient's daily goals."""
        # Create goals
        DailyGoal.objects.create(
            patient=patient,
            title="Goal 1",
            category="exercise",
            target_value=30,
        )
        DailyGoal.objects.create(
            patient=patient,
            title="Goal 2",
            category="hydration",
            target_value=8,
        )
        
        response = authenticated_client.get("/api/v1/daily-goals/")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_create_daily_goal(self, authenticated_client, patient):
        """Test creating a new daily goal."""
        data = {
            "title": "Walk 10,000 steps",
            "category": "exercise",
            "target_value": 10000,
            "recurrence_days": [0, 1, 2, 3, 4],  # Weekdays
            "reminder_time": "08:00:00",
        }
        
        response = authenticated_client.post("/api/v1/daily-goals/", data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Walk 10,000 steps"
        assert response.data["current_value"] == 0
        assert response.data["is_completed"] is False

    def test_tick_goal(self, authenticated_client, patient):
        """Test ticking (completing) a goal."""
        goal = DailyGoal.objects.create(
            patient=patient,
            title="Meditation",
            category="meditation",
            target_value=15,
        )
        
        response = authenticated_client.post(f"/api/v1/daily-goals/{goal.id}/tick/")
        
        assert response.status_code == status.HTTP_200_OK
        
        goal.refresh_from_db()
        assert goal.is_completed is True
        assert goal.current_value == goal.target_value

    def test_untick_goal(self, authenticated_client, patient):
        """Test unticking (marking incomplete) a goal."""
        goal = DailyGoal.objects.create(
            patient=patient,
            title="Reading",
            category="custom",
            target_value=30,
        )
        goal.tick()
        
        response = authenticated_client.post(f"/api/v1/daily-goals/{goal.id}/untick/")
        
        assert response.status_code == status.HTTP_200_OK
        
        goal.refresh_from_db()
        assert goal.is_completed is False

    def test_get_goal_stats(self, authenticated_client, patient):
        """Test retrieving goal statistics (streak, completion rate)."""
        goal = DailyGoal.objects.create(
            patient=patient,
            title="Daily vitamins",
            category="medication",
            target_value=1,
        )
        
        # Create some progress history
        today = timezone.now().date()
        for i in range(3):
            GoalProgress.objects.create(
                goal=goal,
                date=today - timedelta(days=i),
                completed=True,
                actual_value=1,
            )
        
        response = authenticated_client.get(f"/api/v1/daily-goals/{goal.id}/stats/")
        
        assert response.status_code == status.HTTP_200_OK
        assert "streak" in response.data
        assert "completion_rate" in response.data
        assert response.data["streak"] == 3

    def test_unauthorized_access(self, api_client):
        """Test that unauthenticated users cannot access goals."""
        response = api_client.get("/api/v1/daily-goals/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
