"""
Views for Patient Appointment Management.
Includes list, detail, reschedule, and cancel endpoints for patient appointments.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from apps.appointments.models import Appointment
from apps.appointments.serializers import (
    PatientAppointmentListSerializer,
    PatientAppointmentDetailSerializer,
    PatientAppointmentRescheduleSerializer,
    PatientAppointmentCancelSerializer,
)


class PatientAppointmentManagementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for patient to manage their own appointments.
    
    Endpoints:
    - GET /my-appointments/ - List all patient's appointments
    - GET /my-appointments/{id}/ - Get appointment detail
    - PATCH /my-appointments/{id}/reschedule/ - Reschedule appointment
    - POST /my-appointments/{id}/cancel/ - Cancel appointment
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PatientAppointmentListSerializer
    
    def get_queryset(self):
        """Return only appointments for the authenticated user's patient profile."""
        try:
            patient = self.request.user.patient
            return Appointment.objects.filter(
                patient=patient
            ).select_related('hospital').order_by('appointment_datetime')
        except:
            return Appointment.objects.none()
    
    def get_object(self):
        """Override to check patient permission at object level."""
        obj = super().get_object()
        if obj.patient != self.request.user.patient:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to access this appointment.")
        return obj
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return PatientAppointmentDetailSerializer
        elif self.action == 'reschedule':
            return PatientAppointmentRescheduleSerializer
        elif self.action == 'cancel':
            return PatientAppointmentCancelSerializer
        return PatientAppointmentListSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List all appointments for the patient with optional filtering.
        
        Query Parameters:
        - status: Filter by status (scheduled, confirmed, completed, cancelled)
        - appointment_type: Filter by type (follow_up, medication_review, etc.)
        - upcoming: true/false - Show only upcoming/past appointments
        - past: true/false - Show only past appointments
        """
        queryset = self.get_queryset()
        
        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by appointment type if provided
        appointment_type = request.query_params.get('appointment_type')
        if appointment_type:
            queryset = queryset.filter(appointment_type=appointment_type)
        
        # Filter by upcoming/past
        upcoming = request.query_params.get('upcoming')
        past = request.query_params.get('past')
        
        if upcoming and upcoming.lower() == 'true':
            queryset = queryset.filter(appointment_datetime__gt=timezone.now())
        elif past and past.lower() == 'true':
            queryset = queryset.filter(appointment_datetime__lte=timezone.now())
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def reschedule(self, request, pk=None):
        """
        Reschedule an appointment to a new date/time.
        
        Request body:
        {
            "appointment_datetime": "2026-02-15T10:00:00Z"
        }
        """
        appointment = self.get_object()
        
        # Validate appointment can be rescheduled
        if not appointment.is_upcoming:
            return Response(
                {'detail': 'Cannot reschedule past appointments.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if appointment.status == 'cancelled':
            return Response(
                {'detail': 'Cannot reschedule cancelled appointments.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if appointment.status == 'completed':
            return Response(
                {'detail': 'Cannot reschedule completed appointments.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate new datetime
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Check if the error is about past datetime
            if 'appointment_datetime' in serializer.errors:
                error_msg = str(serializer.errors['appointment_datetime'][0])
                if 'past' in error_msg.lower():
                    return Response(
                        {'detail': error_msg},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Update appointment
        appointment.appointment_datetime = serializer.validated_data['appointment_datetime']
        appointment.save()
        
        # Return updated appointment
        detail_serializer = PatientAppointmentDetailSerializer(appointment)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment.
        
        Request body (optional):
        {
            "cancellation_reason": "Unable to attend due to work"
        }
        """
        appointment = self.get_object()
        
        # Validate appointment can be cancelled
        if not appointment.is_upcoming:
            return Response(
                {'detail': 'Cannot cancel past appointments.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if appointment.status == 'cancelled':
            return Response(
                {'detail': 'Appointment is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if appointment.status == 'completed':
            return Response(
                {'detail': 'Cannot cancel completed appointments.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Update appointment
        appointment.status = 'cancelled'
        appointment.cancelled_at = timezone.now()
        appointment.cancelled_by = 'patient'
        appointment.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')
        appointment.save()
        
        # Return updated appointment
        detail_serializer = PatientAppointmentDetailSerializer(appointment)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)
