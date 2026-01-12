"""
Views for enrollment app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from apps.enrollment.models import Hospital, DischargeSummary
from apps.enrollment.serializers import (
    HospitalSerializer,
    DischargeSummaryListSerializer,
    DischargeSummaryDetailSerializer,
    DischargeSummaryCreateSerializer
)


class HospitalViewSet(viewsets.ModelViewSet):
    """ViewSet for Hospital model."""
    
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hospital_type', 'province', 'district', 'status', 'emr_integration_type']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active hospitals."""
        active_hospitals = self.queryset.filter(status='active')
        serializer = self.get_serializer(active_hospitals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_province(self, request):
        """Get hospitals grouped by province."""
        province = request.query_params.get('province')
        if not province:
            return Response(
                {'error': 'Province parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hospitals = self.queryset.filter(province=province, status='active')
        serializer = self.get_serializer(hospitals, many=True)
        return Response(serializer.data)


class DischargeSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for DischargeSummary model."""
    
    queryset = DischargeSummary.objects.select_related(
        'patient', 'hospital', 'created_by'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        'patient', 'hospital', 'discharge_condition', 'risk_level',
        'follow_up_required'
    ]
    ordering_fields = ['discharge_date', 'created_at']
    ordering = ['-discharge_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return DischargeSummaryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DischargeSummaryCreateSerializer
        return DischargeSummaryDetailSerializer
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high-risk discharge summaries."""
        high_risk_summaries = self.queryset.filter(
            risk_level__in=['high', 'critical']
        )
        serializer = DischargeSummaryListSerializer(high_risk_summaries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get discharge summaries from the last 7 days."""
        days = int(request.query_params.get('days', 7))
        cutoff_date = timezone.now().date() - timedelta(days=days)
        recent_summaries = self.queryset.filter(discharge_date__gte=cutoff_date)
        serializer = DischargeSummaryListSerializer(recent_summaries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def needs_follow_up(self, request):
        """Get discharge summaries that require follow-up."""
        follow_up_summaries = self.queryset.filter(follow_up_required=True)
        serializer = DischargeSummaryListSerializer(follow_up_summaries, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def risk_analysis(self, request, pk=None):
        """Get risk analysis for a specific discharge summary."""
        discharge_summary = self.get_object()
        
        risk_data = {
            'discharge_summary_id': discharge_summary.id,
            'patient_name': f"{discharge_summary.patient.first_name} {discharge_summary.patient.last_name}",
            'risk_level': discharge_summary.risk_level,
            'is_high_risk': discharge_summary.is_high_risk,
            'risk_factors': discharge_summary.risk_factors,
            'warning_signs': discharge_summary.warning_signs,
            'warning_signs_kinyarwanda': discharge_summary.warning_signs_kinyarwanda,
            'days_since_discharge': discharge_summary.days_since_discharge,
            'follow_up_required': discharge_summary.follow_up_required,
            'follow_up_timeframe': discharge_summary.follow_up_timeframe,
            'discharge_condition': discharge_summary.discharge_condition,
            'primary_diagnosis': discharge_summary.primary_diagnosis,
        }
        
        return Response(risk_data)
