"""
Views for Patient app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsAuthenticatedUser
from apps.patients.models import Patient, Address, EmergencyContact
from apps.patients.serializers import (
    PatientListSerializer,
    PatientDetailSerializer,
    PatientCreateSerializer,
    AddressSerializer,
    EmergencyContactSerializer,
)


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patients.
    
    Provides CRUD operations for patients with filtering, search, and ordering.
    """

    queryset = Patient.objects.select_related("enrolled_by", "address").prefetch_related(
        "emergency_contacts"
    )
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "gender", "language_preference", "enrolled_by"]
    search_fields = [
        "first_name",
        "last_name",
        "national_id",
        "phone_number",
        "email",
    ]
    ordering_fields = ["enrolled_date", "last_name", "date_of_birth"]
    ordering = ["-enrolled_date"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return PatientListSerializer
        elif self.action == "create":
            return PatientCreateSerializer
        return PatientDetailSerializer

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a patient (soft delete)."""
        patient = self.get_object()
        patient.is_active = False
        patient.save()
        return Response(
            {"status": "Patient deactivated successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Reactivate a patient."""
        patient = self.get_object()
        patient.is_active = True
        patient.save()
        return Response(
            {"status": "Patient activated successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get patient statistics."""
        total = Patient.objects.count()
        active = Patient.objects.filter(is_active=True).count()
        inactive = total - active
        
        by_gender = {}
        for gender, _ in Patient.GENDER_CHOICES:
            by_gender[gender] = Patient.objects.filter(gender=gender).count()

        return Response({
            "total_patients": total,
            "active_patients": active,
            "inactive_patients": inactive,
            "by_gender": by_gender,
        })
    
    @action(detail=True, methods=["get"])
    def export_data(self, request, pk=None):
        """
        Export all patient data (GDPR right to data portability).
        GET /api/v1/patients/{id}/export-data/
        """
        patient = self.get_object()
        
        # Collect all patient-related data
        from apps.consents.serializers import ConsentSerializer, PrivacyPreferenceSerializer
        
        data = {
            'patient': PatientDetailSerializer(patient).data,
            'consents': ConsentSerializer(patient.consents.all(), many=True).data,
            'privacy_preferences': None,
            'appointments': [],
            'prescriptions': [],
            'discharge_summaries': [],
        }
        
        # Add privacy preferences if they exist
        if hasattr(patient, 'privacy_preference'):
            data['privacy_preferences'] = PrivacyPreferenceSerializer(patient.privacy_preference).data
        
        # Add appointments if any
        if hasattr(patient, 'appointments'):
            from apps.appointments.serializers import AppointmentSerializer
            data['appointments'] = AppointmentSerializer(patient.appointments.all(), many=True).data
        
        return Response(data)
    
    @action(detail=True, methods=["post"])
    def request_deletion(self, request, pk=None):
        """
        Request patient data deletion (GDPR right to be forgotten).
        POST /api/v1/patients/{id}/request-deletion/
        
        In production, this should trigger a review process rather than immediate deletion.
        """
        patient = self.get_object()
        
        # In production: Create a deletion request ticket and notify administrators
        # For now, we'll just mark the patient as inactive and log the request
        
        patient.is_active = False
        patient.save()
        
        # Log the deletion request in consent audit logs if consent exists
        from apps.consents.models import ConsentAuditLog
        consents = patient.consents.all()
        for consent in consents:
            ConsentAuditLog.objects.create(
                consent=consent,
                action='exported',
                performed_by='patient',
                details='Data deletion requested by patient (GDPR right to erasure)'
            )
        
        return Response({
            'message': 'Data deletion request submitted successfully',
            'detail': 'Your request is being processed. You will be notified once completed.',
            'patient_id': patient.id,
            'status': 'pending_review'
        })


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing patient addresses."""

    queryset = Address.objects.select_related("patient")
    serializer_class = AddressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["province", "district", "sector"]


class EmergencyContactViewSet(viewsets.ModelViewSet):
    """ViewSet for managing emergency contacts."""

    queryset = EmergencyContact.objects.select_related("patient")
    serializer_class = EmergencyContactSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["patient", "relationship", "is_primary"]
