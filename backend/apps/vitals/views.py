"""
Views for vitals tracking and health progress charts.
"""
from django.db.models import Q, Avg, Min, Max
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.vitals.models import VitalReading, HealthGoal, HealthTrend
from apps.vitals.serializers import (
    VitalReadingSerializer,
    HealthGoalSerializer,
    HealthTrendSerializer,
)
from apps.patients.models import Patient


class VitalReadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vital readings.
    Supports creating, retrieving, and filtering vital readings.
    """

    serializer_class = VitalReadingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["reading_type", "recorded_at"]

    def get_queryset(self):
        """Get vital readings for a specific patient."""
        patient_id = self.kwargs.get("patient_pk")
        queryset = VitalReading.objects.filter(patient_id=patient_id)

        # Filter by reading type if provided
        reading_type = self.request.query_params.get("reading_type")
        if reading_type:
            queryset = queryset.filter(reading_type=reading_type)

        # Filter by date range if provided
        recorded_after = self.request.query_params.get("recorded_after")
        if recorded_after:
            queryset = queryset.filter(recorded_at__date__gte=recorded_after)

        recorded_before = self.request.query_params.get("recorded_before")
        if recorded_before:
            queryset = queryset.filter(recorded_at__date__lte=recorded_before)

        return queryset.order_by("-recorded_at")

    def create(self, request, *args, **kwargs):
        """Record a new vital reading."""
        patient_id = self.kwargs.get("patient_pk")
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(patient=patient, recorded_by=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def latest(self, request, *args, **kwargs):
        """Get latest reading for each vital type."""
        patient_id = self.kwargs.get("patient_pk")
        vitals = []

        for vital_type in [
            "blood_pressure",
            "heart_rate",
            "temperature",
            "weight",
            "oxygen_saturation",
            "respiratory_rate",
            "blood_glucose",
        ]:
            reading = (
                VitalReading.objects.filter(
                    patient_id=patient_id, reading_type=vital_type
                )
                .order_by("-recorded_at")
                .first()
            )
            if reading:
                vitals.append(VitalReadingSerializer(reading).data)

        return Response(vitals)


class HealthGoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing health goals.
    Supports creating, updating, and tracking health goals for patients.
    """

    serializer_class = HealthGoalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "vital_type"]

    def get_queryset(self):
        """Get health goals for a specific patient."""
        patient_id = self.kwargs.get("patient_pk")
        queryset = HealthGoal.objects.filter(patient_id=patient_id)

        # Filter by status if provided
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        """Create a new health goal for a patient."""
        patient_id = self.kwargs.get("patient_pk")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(patient=patient)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HealthProgressViewSet(viewsets.ViewSet):
    """
    ViewSet for health progress tracking and analytics.
    Provides endpoints for health summaries, trends, and progress reports.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def health_summary(self, request, *args, **kwargs):
        """Get health summary dashboard data."""
        patient_id = self.kwargs.get("patient_pk")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get latest readings for each vital type
        latest_readings = []
        for vital_type in [
            "blood_pressure",
            "heart_rate",
            "temperature",
            "weight",
            "oxygen_saturation",
            "blood_glucose",
        ]:
            reading = (
                VitalReading.objects.filter(
                    patient_id=patient_id, reading_type=vital_type
                )
                .order_by("-recorded_at")
                .first()
            )
            if reading:
                latest_readings.append(VitalReadingSerializer(reading).data)

        # Get active goals
        active_goals = HealthGoal.objects.filter(
            patient_id=patient_id, status="active"
        ).count()

        return Response(
            {
                "patient_id": patient_id,
                "patient_name": patient.full_name,
                "latest_readings": latest_readings,
                "active_goals": active_goals,
                "total_readings": VitalReading.objects.filter(
                    patient_id=patient_id
                ).count(),
            }
        )

    @action(detail=False, methods=["get"])
    def vital_trends(self, request, *args, **kwargs):
        """Get vital trends for charting."""
        patient_id = self.kwargs.get("patient_pk")
        reading_type = request.query_params.get("reading_type", "heart_rate")
        days = int(request.query_params.get("days", 7))

        try:
            Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get readings from past N days
        start_date = timezone.now() - timedelta(days=days)
        readings = VitalReading.objects.filter(
            patient_id=patient_id,
            reading_type=reading_type,
            recorded_at__gte=start_date,
        ).order_by("recorded_at")

        # Calculate trend direction
        if readings.count() >= 2:
            first_value = readings.first().value
            last_value = readings.last().value
            if last_value < first_value:
                trend_direction = "improving"
            elif last_value > first_value:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "insufficient_data"

        # Aggregate stats
        stats = readings.aggregate(
            avg_value=Avg("value"),
            min_value=Min("value"),
            max_value=Max("value"),
        )

        return Response(
            {
                "readings": VitalReadingSerializer(readings, many=True).data,
                "trend_direction": trend_direction,
                "stats": stats,
                "period_days": days,
            }
        )

    @action(detail=False, methods=["get"])
    def vital_summary(self, request, *args, **kwargs):
        """Get comprehensive vital summary for all types."""
        patient_id = self.kwargs.get("patient_pk")

        try:
            Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        summary = {}
        for vital_type in [
            "blood_pressure",
            "heart_rate",
            "temperature",
            "weight",
            "oxygen_saturation",
            "blood_glucose",
        ]:
            latest = (
                VitalReading.objects.filter(
                    patient_id=patient_id, reading_type=vital_type
                )
                .order_by("-recorded_at")
                .first()
            )
            if latest:
                summary[vital_type] = VitalReadingSerializer(latest).data

        return Response(summary)

    @action(detail=False, methods=["get"])
    def health_report(self, request, *args, **kwargs):
        """Generate comprehensive health report."""
        patient_id = self.kwargs.get("patient_pk")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get readings from last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        readings = VitalReading.objects.filter(
            patient_id=patient_id,
            recorded_at__gte=thirty_days_ago,
        )

        return Response(
            {
                "patient_name": patient.full_name,
                "patient_id": patient_id,
                "period": "Last 30 days",
                "total_readings": readings.count(),
                "readings_by_type": {
                    vital_type: readings.filter(
                        reading_type=vital_type
                    ).count()
                    for vital_type in [
                        "blood_pressure",
                        "heart_rate",
                        "temperature",
                        "weight",
                        "oxygen_saturation",
                        "blood_glucose",
                    ]
                },
            }
        )

    @action(detail=False, methods=["get"])
    def vital_alerts(self, request, *args, **kwargs):
        """Get abnormal vital readings that need attention."""
        patient_id = self.kwargs.get("patient_pk")

        try:
            Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get recent readings (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_readings = VitalReading.objects.filter(
            patient_id=patient_id,
            recorded_at__gte=seven_days_ago,
        ).order_by("-recorded_at")

        # Identify abnormal readings based on type
        abnormal_readings = []
        for reading in recent_readings:
            is_abnormal = False
            reason = ""

            if reading.reading_type == "temperature" and reading.value > 38:
                is_abnormal = True
                reason = "High fever"
            elif reading.reading_type == "heart_rate" and reading.value > 100:
                is_abnormal = True
                reason = "Elevated heart rate"
            elif reading.reading_type == "blood_pressure" and reading.value > 140:
                is_abnormal = True
                reason = "High blood pressure"
            elif reading.reading_type == "oxygen_saturation" and reading.value < 90:
                is_abnormal = True
                reason = "Low oxygen saturation"

            if is_abnormal:
                abnormal_readings.append(
                    {
                        **VitalReadingSerializer(reading).data,
                        "alert_reason": reason,
                    }
                )

        return Response(
            {
                "abnormal_readings": abnormal_readings,
                "total_abnormal": len(abnormal_readings),
            }
        )

    @action(detail=False, methods=["get"])
    def health_trends(self, request, *args, **kwargs):
        """Get aggregated health trends."""
        patient_id = self.kwargs.get("patient_pk")
        period = request.query_params.get("period", "daily")

        try:
            Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        trends = HealthTrend.objects.filter(
            patient_id=patient_id, period=period
        ).order_by("-period_end")[:10]

        return Response(HealthTrendSerializer(trends, many=True).data)
