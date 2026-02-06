"""
Views for nursing app - Nurse dashboard and alert triage system.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Avg, F
from datetime import timedelta

from .models import NurseProfile, PatientAlert, NursePatientAssignment, AlertLog
from .serializers import (
    NurseProfileSerializer,
    PatientAlertSerializer,
    PatientAlertListSerializer,
    PatientAlertCreateSerializer,
    NursePatientAssignmentSerializer,
    AlertLogSerializer
)
from apps.patients.models import Patient
from apps.core.permissions import IsNurseOrAdmin


class NurseProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing nurse profiles."""
    queryset = NurseProfile.objects.all().select_related('user')
    serializer_class = NurseProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get list of nurses available for assignment."""
        available_nurses = self.queryset.filter(
            is_active=True,
            status='available'
        ).annotate(
            assigned_count=Count('patient_assignments', filter=Q(
                patient_assignments__status__in=['active', 'pending']
            ))
        ).filter(
            assigned_count__lt=F('max_concurrent_patients')
        )
        
        serializer = self.get_serializer(available_nurses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def workload(self, request, pk=None):
        """Get nurse's current workload statistics."""
        nurse = self.get_object()
        
        active_assignments = NursePatientAssignment.objects.filter(
            nurse=nurse,
            status__in=['active', 'pending']
        ).count()
        
        active_alerts = PatientAlert.objects.filter(
            assigned_nurse=nurse,
            status__in=['new', 'assigned', 'in_progress']
        ).count()
        
        overdue_alerts = PatientAlert.objects.filter(
            assigned_nurse=nurse,
            status__in=['new', 'assigned', 'in_progress'],
            sla_deadline__lt=timezone.now()
        ).count()
        
        return Response({
            'nurse': self.get_serializer(nurse).data,
            'active_assignments': active_assignments,
            'active_alerts': active_alerts,
            'overdue_alerts': overdue_alerts,
            'capacity': f"{active_assignments}/{nurse.max_concurrent_patients}"
        })


class PatientAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for managing patient alerts."""
    queryset = PatientAlert.objects.all().select_related(
        'patient', 'assigned_nurse__user', 'discharge_summary', 'appointment'
    )
    permission_classes = [IsAuthenticated]  # Changed from IsNurseOrAdmin to allow patients
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PatientAlertCreateSerializer
        # Always use the full serializer for list and detail
        return PatientAlertSerializer
    
    def get_queryset(self):
        queryset = PatientAlert.objects.all().select_related(
            'patient', 'assigned_nurse__user', 'discharge_summary', 'appointment'
        )
        
        # If user is a patient, filter to only their alerts
        if hasattr(self.request.user, 'patient'):
            patient = self.request.user.patient
            queryset = queryset.filter(patient=patient)
            print(f'🔐 [PATIENT ALERT FILTER] Patient {patient.id} - {patient.full_name}')
        else:
            # For nurses/admins, allow filtering by patient_id parameter
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                try:
                    from apps.patients.models import Patient
                    patient = Patient.objects.get(id=patient_id)
                    queryset = queryset.filter(patient=patient)
                except Patient.DoesNotExist:
                    pass
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by alert_type
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        # Filter by assigned nurse
        nurse_id = self.request.query_params.get('nurse_id')
        if nurse_id:
            queryset = queryset.filter(assigned_nurse_id=nurse_id)
        
        # Filter overdue
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(
                status__in=['new', 'assigned', 'in_progress'],
                sla_deadline__lt=timezone.now()
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Create alert and log the action."""
        alert = serializer.save()
        AlertLog.objects.create(
            alert=alert,
            action='created',
            performed_by=self.request.user,
            notes=f"Alert created: {alert.title}"
        )
    
    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """Assign alert to a nurse."""
        alert = self.get_object()
        nurse_id = request.data.get('nurse_id')
        
        # Cannot assign resolved alerts
        if alert.status == 'resolved':
            return Response(
                {'error': 'Cannot assign an already resolved alert'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not nurse_id:
            return Response(
                {'error': 'nurse_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nurse = NurseProfile.objects.get(id=nurse_id)
        except NurseProfile.DoesNotExist:
            return Response(
                {'error': 'Nurse not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if nurse is available
        if not nurse.is_available_for_assignment:
            return Response(
                {'error': 'Nurse is not available for assignment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.assigned_nurse = nurse
        alert.assigned_at = timezone.now()
        alert.status = 'assigned'
        alert.save()
        
        # Log the action
        AlertLog.objects.create(
            alert=alert,
            action='assigned',
            performed_by=request.user,
            notes=f"Assigned to {nurse.user.get_full_name()}"
        )
        
        return Response(PatientAlertSerializer(alert).data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert (nurse starts working on it)."""
        alert = self.get_object()
        
        if alert.status == 'new':
            alert.status = 'assigned'
        
        alert.acknowledged_at = timezone.now()
        alert.status = 'in_progress'
        alert.save()
        
        AlertLog.objects.create(
            alert=alert,
            action='acknowledged',
            performed_by=request.user,
            notes=request.data.get('notes', 'Alert acknowledged')
        )
        
        return Response(PatientAlertSerializer(alert).data)
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """Resolve an alert."""
        alert = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        # Validate that resolution_notes is provided
        if not resolution_notes or resolution_notes.strip() == '':
            return Response(
                {'error': 'resolution_notes is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cannot resolve already resolved alerts
        if alert.status == 'resolved':
            return Response(
                {'error': 'Cannot resolve an already resolved alert'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.resolution_notes = resolution_notes
        alert.save()
        
        AlertLog.objects.create(
            alert=alert,
            action='resolved',
            performed_by=request.user,
            notes=resolution_notes or 'Alert resolved'
        )
        
        return Response(PatientAlertSerializer(alert).data)
    
    @action(detail=True, methods=['patch'])
    def escalate(self, request, pk=None):
        """Escalate an alert to higher severity."""
        alert = self.get_object()
        escalation_reason = request.data.get('escalation_reason', '')
        
        # Validate that escalation_reason is provided
        if not escalation_reason or escalation_reason.strip() == '':
            return Response(
                {'error': 'escalation_reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cannot escalate already resolved alerts
        if alert.status == 'resolved':
            return Response(
                {'error': 'Cannot escalate an already resolved alert'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Increase severity
        severity_levels = ['low', 'medium', 'high', 'critical']
        current_index = severity_levels.index(alert.severity)
        if current_index < len(severity_levels) - 1:
            alert.severity = severity_levels[current_index + 1]
            alert.status = 'escalated'
            alert.escalation_reason = escalation_reason
            
            # Update SLA deadline based on new severity
            sla_minutes = {
                'critical': 10,
                'high': 30,
                'medium': 120,
                'low': 240,
            }
            alert.sla_deadline = timezone.now() + timedelta(
                minutes=sla_minutes.get(alert.severity, 240)
            )
            alert.save()
            
            AlertLog.objects.create(
                alert=alert,
                action='escalated',
                performed_by=request.user,
                notes=escalation_reason or f'Escalated to {alert.severity}'
            )
            
            return Response(PatientAlertSerializer(alert).data)
        else:
            return Response(
                {'error': 'Alert is already at highest severity'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get dashboard statistics for alerts."""
        now = timezone.now()
        
        # Total alerts by status
        status_counts = {}
        for status_choice in PatientAlert.STATUS_CHOICES:
            count = self.queryset.filter(status=status_choice[0]).count()
            status_counts[status_choice[0]] = count
        
        # Severity distribution for active alerts
        severity_counts = {}
        active_statuses = ['new', 'assigned', 'in_progress', 'escalated']
        for severity_choice in PatientAlert.SEVERITY_CHOICES:
            count = self.queryset.filter(
                status__in=active_statuses,
                severity=severity_choice[0]
            ).count()
            severity_counts[severity_choice[0]] = count
        
        # Overdue alerts
        overdue_count = self.queryset.filter(
            status__in=active_statuses,
            sla_deadline__lt=now
        ).count()
        
        # Average response time (in minutes)
        avg_response = PatientAlert.objects.filter(
            acknowledged_at__isnull=False
        ).annotate(
            response_time=F('acknowledged_at') - F('created_at')
        ).aggregate(
            avg_response=Avg('response_time')
        )['avg_response']
        
        if avg_response:
            avg_response_minutes = avg_response.total_seconds() / 60
        else:
            avg_response_minutes = None
        
        # Average resolution time
        avg_resolution = PatientAlert.objects.filter(
            resolved_at__isnull=False
        ).annotate(
            resolution_time=F('resolved_at') - F('created_at')
        ).aggregate(
            avg_resolution=Avg('resolution_time')
        )['avg_resolution']
        
        if avg_resolution:
            avg_resolution_minutes = avg_resolution.total_seconds() / 60
        else:
            avg_resolution_minutes = None
        
        return Response({
            'status_counts': status_counts,
            'severity_counts': severity_counts,
            'overdue_count': overdue_count,
            'avg_response_time_minutes': avg_response_minutes,
            'avg_resolution_time_minutes': avg_resolution_minutes,
            'total_active': sum(severity_counts.values())
        })
    
    @action(detail=False, methods=['get'])
    def my_queue(self, request):
        """Get alerts assigned to the current user (if they're a nurse)."""
        try:
            nurse_profile = NurseProfile.objects.get(user=request.user)
        except NurseProfile.DoesNotExist:
            return Response(
                {'error': 'User is not a registered nurse'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        alerts = self.queryset.filter(
            assigned_nurse=nurse_profile,
            status__in=['assigned', 'in_progress', 'escalated']
        ).order_by('sla_deadline', '-severity')
        
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get placeholder for stats - not a valid endpoint by itself"""
        return Response(
            {'error': 'Use /stats/overview/ or /stats/by-severity/'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'], url_path='stats/overview')
    def stats_overview(self, request):
        """Get alert dashboard statistics overview."""
        now = timezone.now()
        
        # Count alerts by status
        stats = {
            'total_alerts': self.queryset.count(),
            'new_count': self.queryset.filter(status='new').count(),
            'assigned_count': self.queryset.filter(status='assigned').count(),
            'in_progress_count': self.queryset.filter(status='in_progress').count(),
            'resolved_count': self.queryset.filter(status='resolved').count(),
            'escalated_count': self.queryset.filter(status='escalated').count(),
            'closed_count': self.queryset.filter(status='closed').count(),
            'overdue_count': self.queryset.filter(
                status__in=['new', 'assigned', 'in_progress'],
                sla_deadline__lt=now
            ).count(),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'], url_path='stats/by-severity')
    def stats_by_severity(self, request):
        """Get alert statistics grouped by severity."""
        stats = {}
        for severity, _ in PatientAlert.SEVERITY_CHOICES:
            stats[severity] = self.queryset.filter(severity=severity).count()
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get audit history for an alert."""
        alert = self.get_object()
        logs = alert.logs.all().order_by('-timestamp')
        serializer = AlertLogSerializer(logs, many=True)
        return Response(serializer.data)


class NursePatientAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing nurse-patient assignments."""
    queryset = NursePatientAssignment.objects.all().select_related(
        'nurse__user', 'patient', 'discharge_summary'
    )
    serializer_class = NursePatientAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by nurse
        nurse_id = self.request.query_params.get('nurse_id')
        if nurse_id:
            queryset = queryset.filter(nurse_id=nurse_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_patients(self, request):
        """Get patients assigned to the current user (if they're a nurse)."""
        try:
            nurse_profile = NurseProfile.objects.get(user=request.user)
        except NurseProfile.DoesNotExist:
            return Response(
                {'error': 'User is not a registered nurse'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        assignments = self.queryset.filter(
            nurse=nurse_profile,
            status__in=['active', 'pending']
        ).order_by('-priority', '-assigned_at')
        
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)


class AlertLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing alert logs (read-only)."""
    queryset = AlertLog.objects.all().select_related(
        'alert', 'performed_by'
    )
    serializer_class = AlertLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by alert
        alert_id = self.request.query_params.get('alert_id')
        if alert_id:
            queryset = queryset.filter(alert_id=alert_id)
        
        return queryset
