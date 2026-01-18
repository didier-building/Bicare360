from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from apps.medications.models import Medication, Prescription, MedicationAdherence
from apps.medications.serializers import (
    MedicationSerializer,
    PrescriptionListSerializer,
    PrescriptionDetailSerializer,
    PrescriptionCreateSerializer,
    MedicationAdherenceSerializer,
)
from apps.core.permissions import IsAuthenticatedUser


class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medications"""
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dosage_form', 'requires_prescription', 'is_active']
    search_fields = ['name', 'generic_name', 'brand_name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active medications"""
        active_meds = self.queryset.filter(is_active=True)
        page = self.paginate_queryset(active_meds)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(active_meds, many=True)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing prescriptions"""
    queryset = Prescription.objects.all().select_related('patient', 'medication', 'discharge_summary')
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'medication', 'is_active', 'route']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PrescriptionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PrescriptionCreateSerializer
        return PrescriptionDetailSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get prescriptions that are currently active and within date range"""
        today = timezone.now().date()
        current_prescriptions = self.queryset.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )
        
        page = self.paginate_queryset(current_prescriptions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(current_prescriptions, many=True)
        return Response(serializer.data)


class MedicationAdherenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medication adherence records"""
    queryset = MedicationAdherence.objects.all().select_related('prescription', 'patient', 'prescription__medication')
    serializer_class = MedicationAdherenceSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['prescription', 'patient', 'status', 'scheduled_date']
    ordering_fields = ['scheduled_date', 'scheduled_time', 'created_at']
    ordering = ['-scheduled_date', '-scheduled_time']
    
    @action(detail=True, methods=['post'])
    def mark_taken(self, request, pk=None):
        """Mark an adherence record as taken"""
        adherence = self.get_object()
        adherence.status = 'taken'
        adherence.taken_at = timezone.now()
        adherence.save()
        
        serializer = self.get_serializer(adherence)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_missed(self, request, pk=None):
        """Mark an adherence record as missed with optional reason"""
        adherence = self.get_object()
        adherence.status = 'missed'
        adherence.reason_missed = request.data.get('reason', '')
        adherence.save()
        
        serializer = self.get_serializer(adherence)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue adherence records (scheduled but not taken)"""
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        
        # Get scheduled records that are overdue
        overdue_records = self.queryset.filter(
            status='scheduled'
        ).filter(
            scheduled_date__lt=today
        ) | self.queryset.filter(
            status='scheduled',
            scheduled_date=today,
            scheduled_time__lt=current_time
        )
        
        page = self.paginate_queryset(overdue_records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(overdue_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get adherence statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        total = queryset.count()
        taken = queryset.filter(status='taken').count()
        missed = queryset.filter(status='missed').count()
        skipped = queryset.filter(status='skipped').count()
        scheduled = queryset.filter(status='scheduled').count()
        late = queryset.filter(status='late').count()
        
        adherence_rate = (taken / total * 100) if total > 0 else 0
        
        return Response({
            'total': total,
            'taken': taken,
            'missed': missed,
            'skipped': skipped,
            'scheduled': scheduled,
            'late': late,
            'adherence_rate': round(adherence_rate, 2)
        })
