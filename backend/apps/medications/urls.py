from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.medications.views import MedicationViewSet, PrescriptionViewSet, MedicationAdherenceViewSet

router = DefaultRouter()
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'adherence', MedicationAdherenceViewSet, basename='medicationadherence')

app_name = 'medications'

urlpatterns = [
    path('', include(router.urls)),
]
