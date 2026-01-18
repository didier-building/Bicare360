"""
Views for consent management and GDPR compliance.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.consents.models import ConsentVersion, Consent, PrivacyPreference, ConsentAuditLog
from apps.consents.serializers import (
    ConsentVersionSerializer,
    ConsentSerializer,
    ConsentListSerializer,
    ConsentDetailSerializer,
    ConsentCreateSerializer,
    PrivacyPreferenceSerializer,
    ConsentAuditLogSerializer,
)
from apps.core.permissions import IsAuthenticatedUser


class ConsentVersionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing consent versions.
    Allows CRUD operations on consent text versions.
    """
    queryset = ConsentVersion.objects.all()
    serializer_class = ConsentVersionSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['consent_type', 'is_active']
    ordering_fields = ['effective_date', 'version_number']
    ordering = ['consent_type', '-version_number']


class ConsentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patient consents.
    Supports CRUD operations and consent revocation.
    """
    queryset = Consent.objects.select_related('patient', 'consent_version').all()
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['patient', 'granted', 'consent_version__consent_type']
    search_fields = ['patient__first_name', 'patient__last_name', 'notes']
    ordering_fields = ['granted_date', 'revoked_date']
    ordering = ['-granted_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ConsentListSerializer
        elif self.action == 'retrieve':
            return ConsentDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ConsentCreateSerializer
        return ConsentSerializer
    
    def perform_create(self, serializer):
        """Create consent and log the action."""
        consent = serializer.save()
        
        # Create audit log entry
        ConsentAuditLog.objects.create(
            consent=consent,
            action='granted' if consent.granted else 'revoked',
            performed_by='system',  # TODO: Use request.user when auth is implemented
            details=f'Consent {"granted" if consent.granted else "revoked"} via API'
        )
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoke a consent.
        POST /api/v1/consents/{id}/revoke/
        """
        consent = self.get_object()
        consent.granted = False
        consent.revoked_date = timezone.now()
        consent.save()
        
        # Create audit log entry
        ConsentAuditLog.objects.create(
            consent=consent,
            action='revoked',
            performed_by='system',  # TODO: Use request.user
            details='Consent revoked via API'
        )
        
        serializer = self.get_serializer(consent)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active consents.
        GET /api/v1/consents/active/
        """
        active_consents = self.queryset.filter(granted=True, revoked_date__isnull=True)
        
        page = self.paginate_queryset(active_consents)
        if page is not None:
            serializer = ConsentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ConsentListSerializer(active_consents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def audit_logs(self, request, pk=None):
        """
        Get audit logs for a specific consent.
        GET /api/v1/consents/{id}/audit-logs/
        """
        consent = self.get_object()
        logs = consent.audit_logs.all()
        serializer = ConsentAuditLogSerializer(logs, many=True)
        return Response(serializer.data)


class PrivacyPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patient privacy preferences.
    One-to-one relationship with Patient.
    """
    queryset = PrivacyPreference.objects.select_related('patient').all()
    serializer_class = PrivacyPreferenceSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient', 'preferred_contact_method']


class ConsentAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing consent audit logs.
    Read-only - logs are created automatically by the system.
    """
    queryset = ConsentAuditLog.objects.select_related('consent', 'consent__patient').all()
    serializer_class = ConsentAuditLogSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action', 'consent', 'performed_by']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
