from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from apps.medications.models import (
    Medication, Prescription, MedicationAdherence, PatientMedicationTracker,
    SymptomReport, PrescriptionRefillRequest
)
from apps.medications.serializers import (
    MedicationSerializer,
    PrescriptionListSerializer,
    PrescriptionDetailSerializer,
    PrescriptionCreateSerializer,
    MedicationAdherenceSerializer,
    PatientMedicationTrackerSerializer,
    SymptomReportSerializer,
    PrescriptionRefillRequestSerializer,
)
from apps.core.permissions import IsAuthenticatedUser
from apps.patients.models import Patient


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
    
    def get_queryset(self):
        """Filter prescriptions based on user type."""
        queryset = Prescription.objects.all().select_related('patient', 'medication', 'discharge_summary')
        if hasattr(self.request.user, 'patient'):
            patient = self.request.user.patient
            queryset = queryset.filter(patient=patient)
            print(f'🔐 [PRESCRIPTION FILTER] Patient {patient.id} - {patient.full_name}')
        else:
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                try:
                    patient = Patient.objects.get(id=patient_id)
                    queryset = queryset.filter(patient=patient)
                except Patient.DoesNotExist:
                    pass
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['list', 'current']:
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
        ).select_related('patient', 'medication')[:50]  # Limit to 50 for performance
        
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
    
    def get_queryset(self):
        """Filter adherence records based on user type."""
        queryset = MedicationAdherence.objects.all().select_related('prescription', 'patient', 'prescription__medication')
        if hasattr(self.request.user, 'patient'):
            patient = self.request.user.patient
            queryset = queryset.filter(patient=patient)
            print(f'🔐 [ADHERENCE FILTER] Patient {patient.id} - {patient.full_name}')
        else:
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                try:
                    patient = Patient.objects.get(id=patient_id)
                    queryset = queryset.filter(patient=patient)
                except Patient.DoesNotExist:
                    pass
        return queryset
    
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


class PatientMedicationTrackerViewSet(viewsets.ModelViewSet):
    """ViewSet for patient medication tracking"""
    queryset = PatientMedicationTracker.objects.all().select_related('patient', 'prescription__medication')
    serializer_class = PatientMedicationTrackerSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'prescription', 'status', 'date']
    ordering_fields = ['date', 'reported_at']
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter tracking records based on user permissions"""
        if hasattr(self.request.user, 'patient'):
            # Patients only see their own tracking records
            return self.queryset.filter(patient=self.request.user.patient)
        return self.queryset
    
    def perform_create(self, serializer):
        """Auto-assign patient when creating tracking record"""
        if hasattr(self.request.user, 'patient'):
            serializer.save(patient=self.request.user.patient)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's medication tracking for current patient"""
        if not hasattr(request.user, 'patient'):
            return Response({'error': 'Only patients can access this endpoint'}, status=400)
        
        today = timezone.now().date()
        tracking_records = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(tracking_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_taken(self, request):
        """Mark medication as taken for today"""
        if not hasattr(request.user, 'patient'):
            return Response({'error': 'Only patients can access this endpoint'}, status=400)
        
        prescription_id = request.data.get('prescription_id')
        taken_time = request.data.get('taken_time', timezone.now().time())
        
        if not prescription_id:
            return Response({'error': 'prescription_id is required'}, status=400)
        
        today = timezone.now().date()
        tracker, created = PatientMedicationTracker.objects.get_or_create(
            patient=request.user.patient,
            prescription_id=prescription_id,
            date=today,
            defaults={'status': 'taken', 'taken_time': taken_time}
        )
        
        if not created:
            tracker.status = 'taken'
            tracker.taken_time = taken_time
            tracker.save()
        
        serializer = self.get_serializer(tracker)
        return Response(serializer.data)


class SymptomReportViewSet(viewsets.ModelViewSet):
    """ViewSet for patient symptom reports"""
    queryset = SymptomReport.objects.all().select_related('patient', 'related_prescription__medication')
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'symptom_type', 'severity', 'reviewed_by_nurse']
    ordering_fields = ['reported_at', 'severity']
    ordering = ['-reported_at']
    
    def get_serializer_class(self):
        return SymptomReportSerializer
    
    def get_queryset(self):
        """Filter reports based on user permissions"""
        if hasattr(self.request.user, 'patient'):
            # Patients only see their own reports
            return self.queryset.filter(patient=self.request.user.patient)
        return self.queryset
    
    def perform_create(self, serializer):
        """Auto-assign patient when creating report"""
        if hasattr(self.request.user, 'patient'):
            serializer.save(patient=self.request.user.patient)
        else:
            serializer.save()


class PrescriptionRefillRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for prescription refill requests"""
    queryset = PrescriptionRefillRequest.objects.all().select_related('patient', 'prescription__medication', 'reviewed_by')
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'prescription', 'status', 'urgent']
    ordering_fields = ['requested_at', 'status']
    ordering = ['-requested_at']
    
    def get_serializer_class(self):
        return PrescriptionRefillRequestSerializer
    
    def get_queryset(self):
        """Filter requests based on user permissions"""
        if hasattr(self.request.user, 'patient'):
            # Patients only see their own requests
            return self.queryset.filter(patient=self.request.user.patient)
        return self.queryset
    
    def perform_create(self, serializer):
        """Auto-assign patient when creating request"""
        if hasattr(self.request.user, 'patient'):
            serializer.save(patient=self.request.user.patient)
        else:
            serializer.save()
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve a refill request"""
        refill_request = self.get_object()
        refill_request.status = 'approved'
        refill_request.reviewed_by = request.user
        refill_request.reviewed_at = timezone.now()
        refill_request.review_notes = request.data.get('review_notes', '')
        refill_request.save()
        
        serializer = self.get_serializer(refill_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def deny(self, request, pk=None):
        """Deny a refill request"""
        refill_request = self.get_object()
        refill_request.status = 'denied'
        refill_request.reviewed_by = request.user
        refill_request.reviewed_at = timezone.now()
        refill_request.review_notes = request.data.get('review_notes', '')
        refill_request.save()
        
        serializer = self.get_serializer(refill_request)
        return Response(serializer.data)
