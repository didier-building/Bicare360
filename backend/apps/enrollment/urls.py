"""
URL configuration for enrollment app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.enrollment.views import HospitalViewSet, DischargeSummaryViewSet

router = DefaultRouter()
router.register(r'hospitals', HospitalViewSet, basename='hospital')
router.register(r'discharge-summaries', DischargeSummaryViewSet, basename='dischargesummary')

app_name = 'enrollment'

urlpatterns = [
    path('', include(router.urls)),
]
