"""
URL configuration for appointments app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.appointments.views import AppointmentViewSet, AppointmentReminderViewSet
from apps.appointments.views_patient_appointments import PatientAppointmentManagementViewSet

app_name = 'appointments'

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'appointment-reminders', AppointmentReminderViewSet, basename='appointmentreminder')

# Patient-specific appointments - register with full path to avoid conflicts
patient_router = DefaultRouter()
patient_router.register(r'appointments/my-appointments', PatientAppointmentManagementViewSet, basename='patient-appointment')

urlpatterns = [
    path('', include(patient_router.urls)),  # Must come first (more specific)
    path('', include(router.urls)),
]
