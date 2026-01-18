"""
URL configuration for appointments app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.appointments.views import AppointmentViewSet, AppointmentReminderViewSet

app_name = 'appointments'

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'appointment-reminders', AppointmentReminderViewSet, basename='appointmentreminder')

urlpatterns = [
    path('', include(router.urls)),
]
