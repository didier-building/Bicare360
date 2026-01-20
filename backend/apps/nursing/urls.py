"""
URL configuration for nursing app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NurseProfileViewSet,
    PatientAlertViewSet,
    NursePatientAssignmentViewSet,
    AlertLogViewSet
)

router = DefaultRouter()
router.register(r'nurses', NurseProfileViewSet, basename='nurseprofile')
router.register(r'alerts', PatientAlertViewSet, basename='patientalert')
router.register(r'assignments', NursePatientAssignmentViewSet, basename='nursepatientassignment')
router.register(r'logs', AlertLogViewSet, basename='alertlog')

urlpatterns = [
    path('', include(router.urls)),
]
