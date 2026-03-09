"""
URL routing for vitals and health progress endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.vitals.views import (
    VitalReadingViewSet,
    HealthGoalViewSet,
    HealthProgressViewSet,
    DailyGoalViewSet,
)

# Router for nested resources under patients
vitals_router = DefaultRouter()
vitals_router.register(r"vital-readings", VitalReadingViewSet, basename="vital-reading")
vitals_router.register(r"health-goals", HealthGoalViewSet, basename="health-goal")
vitals_router.register(r"health-progress", HealthProgressViewSet, basename="health-progress")
vitals_router.register(r"daily-goals", DailyGoalViewSet, basename="daily-goal")

urlpatterns = [
    path("", include(vitals_router.urls)),
]
