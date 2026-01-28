"""URL configuration for caregivers app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.caregivers.views import CaregiverViewSet, CaregiverBookingViewSet, CaregiverReviewViewSet

router = DefaultRouter()
router.register(r'caregivers', CaregiverViewSet, basename='caregiver')
router.register(r'bookings', CaregiverBookingViewSet, basename='booking')
router.register(r'reviews', CaregiverReviewViewSet, basename='review')

urlpatterns = router.urls
