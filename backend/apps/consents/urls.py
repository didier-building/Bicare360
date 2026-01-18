"""
URL configuration for consent management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.consents import views

app_name = 'consents'

router = DefaultRouter()
router.register(r'consent-versions', views.ConsentVersionViewSet, basename='consentversion')
router.register(r'consents', views.ConsentViewSet, basename='consent')
router.register(r'privacy-preferences', views.PrivacyPreferenceViewSet, basename='privacypreference')
router.register(r'consent-audit-logs', views.ConsentAuditLogViewSet, basename='consentauditlog')

urlpatterns = [
    path('', include(router.urls)),
]
