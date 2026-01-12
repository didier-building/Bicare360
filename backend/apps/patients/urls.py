"""
URL configuration for Patient app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.patients.views import PatientViewSet, AddressViewSet, EmergencyContactViewSet

app_name = "patients"

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"addresses", AddressViewSet, basename="address")
router.register(r"emergency-contacts", EmergencyContactViewSet, basename="emergency-contact")

urlpatterns = [
    path("", include(router.urls)),
]
