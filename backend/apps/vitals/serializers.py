"""
Serializers for vitals and health progress tracking.
"""
from rest_framework import serializers
from apps.vitals.models import VitalReading, HealthGoal, HealthTrend


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
