"""
Serializers for vitals and health progress tracking.
"""
from rest_framework import serializers
from apps.vitals.models import VitalReading, HealthGoal, HealthTrend, DailyGoal, GoalProgress


class VitalReadingSerializer(serializers.ModelSerializer):
    """Serializer for vital readings."""

    class Meta:
        model = VitalReading
        fields = [
            "id",
            "patient",
            "reading_type",
            "value",
            "secondary_value",
            "unit",
            "recorded_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "patient", "created_at", "updated_at"]


class HealthGoalSerializer(serializers.ModelSerializer):
    """Serializer for health goals."""

    class Meta:
        model = HealthGoal
        fields = [
            "id",
            "patient",
            "vital_type",
            "goal_name",
            "target_value",
            "unit",
            "start_date",
            "target_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "patient", "created_at", "updated_at"]


class HealthTrendSerializer(serializers.ModelSerializer):
    """Serializer for health trends."""

    class Meta:
        model = HealthTrend
        fields = [
            "id",
            "patient",
            "vital_type",
            "period",
            "period_start",
            "period_end",
            "reading_count",
            "average_value",
            "min_value",
            "max_value",
            "median_value",
            "average_secondary_value",
            "min_secondary_value",
            "max_secondary_value",
            "unit",
            "trend_direction",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailyGoalSerializer(serializers.ModelSerializer):
    """Serializer for daily goals (Phase 1B - Daily Goals System)."""

    class Meta:
        model = DailyGoal
        fields = [
            "id",
            "patient",
            "title",
            "category",
            "target_value",
            "current_value",
            "is_completed",
            "completed_at",
            "is_recurring",
            "recurrence_days",
            "reminder_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "patient", "completed_at", "created_at", "updated_at"]

    def create(self, validated_data):
        """Create a daily goal for the authenticated patient."""
        patient = self.context["request"].user.patient
        validated_data["patient"] = patient
        return super().create(validated_data)


class GoalProgressSerializer(serializers.ModelSerializer):
    """Serializer for goal progress records."""

    class Meta:
        model = GoalProgress
        fields = [
            "id",
            "goal",
            "date",
            "completed",
            "actual_value",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GoalStatsSerializer(serializers.Serializer):
    """Serializer for goal statistics (streak, completion rate)."""

    streak = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    total_completions = serializers.IntegerField(required=False)
    last_completed = serializers.DateField(required=False, allow_null=True)
