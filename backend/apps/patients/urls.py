"""
URL configuration for Patient app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from apps.patients.views import (
    PatientViewSet, 
    AddressViewSet, 
    EmergencyContactViewSet,
    patient_register,
    patient_login,
    request_appointment,
)
from apps.vitals.views import VitalReadingViewSet, HealthGoalViewSet, HealthProgressViewSet

app_name = "patients"

# Main router for patients
router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"addresses", AddressViewSet, basename="address")
router.register(r"emergency-contacts", EmergencyContactViewSet, basename="emergency-contact")

# Nested routers for patient-specific resources
patients_router = routers.NestedDefaultRouter(router, r"patients", lookup="patient")
patients_router.register(r"vitals", VitalReadingViewSet, basename="patient-vitals")
patients_router.register(r"health-goals", HealthGoalViewSet, basename="patient-health-goals")
patients_router.register(r"health-progress", HealthProgressViewSet, basename="patient-health-progress")

urlpatterns = [
    # Patient portal authentication endpoints (must come before router)
    path("patients/register/", patient_register, name="patient-register"),
    path("patients/login/", patient_login, name="patient-login"),
    path("patients/appointments/request/", request_appointment, name="patient-appointment-request"),
    # Router URLs
    path("", include(router.urls)),
    path("", include(patients_router.urls)),
]
