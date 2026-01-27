from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.medications.views import (
    MedicationViewSet, PrescriptionViewSet, MedicationAdherenceViewSet,
    PatientMedicationTrackerViewSet, SymptomReportViewSet, PrescriptionRefillRequestViewSet
)

router = DefaultRouter()
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'adherence', MedicationAdherenceViewSet, basename='medicationadherence')
router.register(r'tracking', PatientMedicationTrackerViewSet, basename='patientmedicationtracker')
router.register(r'symptom-reports', SymptomReportViewSet, basename='symptomreport')
router.register(r'refill-requests', PrescriptionRefillRequestViewSet, basename='refillrequest')

app_name = 'medications'

urlpatterns = [
    path('', include(router.urls)),
]
