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

# Patient appointments need their own route since they're nested
appointment_router = DefaultRouter()
appointment_router.register(r'my-appointments', PatientAppointmentManagementViewSet, basename='patient-appointment')

urlpatterns = [
    path('appointments/', include(appointment_router.urls)),
    path('', include(router.urls)),
]
