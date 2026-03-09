"""URL configuration for caregivers app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.caregivers import views

router = DefaultRouter()
router.register(r'caregivers', views.CaregiverViewSet, basename='caregiver')
router.register(r'bookings', views.CaregiverBookingViewSet, basename='booking')
router.register(r'reviews', views.CaregiverReviewViewSet, basename='review')

urlpatterns = [
    path('login/', views.caregiver_login, name='caregiver-login'),
    path('dashboard-stats/', views.caregiver_dashboard_stats, name='caregiver-dashboard-stats'),
    path('', include(router.urls)),
]
