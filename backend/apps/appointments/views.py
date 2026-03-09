"""
Views for appointments app.
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentReminder
from apps.appointments.serializers import (
    AppointmentSerializer,
    AppointmentListSerializer,
    AppointmentDetailSerializer,
    AppointmentCreateSerializer,
    AppointmentReminderSerializer
)
from apps.core.permissions import IsAuthenticatedUser, IsPatient
from apps.messaging.email_service import EmailService
from apps.patients.models import Patient


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments.
    Provides CRUD operations and custom actions.
    """
    queryset = Appointment.objects.select_related('patient', 'hospital').all()
    permission_classes = [IsAuthenticatedUser]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'patient', 'hospital', 'location_type']
    search_fields = ['patient__first_name', 'patient__last_name', 'provider_name', 'reason']
    ordering_fields = ['appointment_datetime', 'created_at']
    ordering = ['appointment_datetime']
    
    def get_queryset(self):
        """
        Filter appointments based on user type.
        - Patients: Only see their own appointments
        - Providers/Admins: Can see all appointments or filter by patient_id
        """
        queryset = Appointment.objects.select_related('patient', 'hospital').all()
        
        # If user is a patient, filter to only their appointments
        if hasattr(self.request.user, 'patient'):
            patient = self.request.user.patient
            queryset = queryset.filter(patient=patient)
            print(f'🔐 [APPOINTMENT FILTER] Patient {patient.id} - {patient.full_name}')
            print(f'   Filtered to {queryset.count()} appointments')
        else:
            # For providers/admins, allow filtering by patient_id parameter
            patient_id = self.request.query_params.get('patient_id', None)
            if patient_id:
                try:
                    patient = Patient.objects.get(id=patient_id)
                    queryset = queryset.filter(patient=patient)
                    print(f'🔐 [APPOINTMENT FILTER] Provider/Admin filtering by patient {patient_id}')
                    print(f'   Filtered to {queryset.count()} appointments')
                except Patient.DoesNotExist:
                    print(f'⚠️ [APPOINTMENT FILTER] Patient {patient_id} not found')
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'list':
            return AppointmentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AppointmentCreateSerializer
        elif self.action == 'retrieve':
            return AppointmentDetailSerializer
        return AppointmentSerializer
    
    def perform_create(self, serializer):
        """Create appointment and send confirmation email to patient."""
        appointment = serializer.save()
        
        # Send appointment confirmation email to patient
        print(f'\n🔵 [APPOINTMENT CREATE] ID: {appointment.id}')
        print(f'   Patient: {appointment.patient.full_name}')
        print(f'   Email: {appointment.patient.email}')
        
        if appointment.patient and appointment.patient.email:
            email_service = EmailService()
            try:
                print(f'   📧 Sending appointment email...')
                result = email_service.send_appointment_reminder_email(
                    patient_email=appointment.patient.email,
                    patient_name=appointment.patient.full_name,
                    appointment_date=appointment.appointment_datetime.strftime('%B %d, %Y'),
                    appointment_time=appointment.appointment_datetime.strftime('%I:%M %p'),
                    hospital_name=appointment.hospital.name,
                    provider_name=appointment.provider_name or 'Healthcare Provider',
                    appointment_type=appointment.get_appointment_type_display()
                )
                print(f'   ✅ Email sent: {result["recipient"]}')
            except Exception as e:
                print(f'   ❌ Failed to send email: {str(e)}')
        else:
            print(f'   ⚠️ No email address for patient')
    
    def perform_update(self, serializer):
        """Update appointment and send updated notification to patient."""
        appointment = serializer.save()
        
        # Send updated appointment notification to patient
        print(f'\n🔵 [APPOINTMENT UPDATE] ID: {appointment.id}')
        print(f'   Patient: {appointment.patient.full_name}')
        print(f'   Email: {appointment.patient.email}')
        
        if appointment.patient and appointment.patient.email:
            email_service = EmailService()
            try:
                print(f'   📧 Sending updated appointment email...')
                result = email_service.send_appointment_reminder_email(
                    patient_email=appointment.patient.email,
                    patient_name=appointment.patient.full_name,
                    appointment_date=appointment.appointment_datetime.strftime('%B %d, %Y'),
                    appointment_time=appointment.appointment_datetime.strftime('%I:%M %p'),
                    hospital_name=appointment.hospital.name,
                    provider_name=appointment.provider_name or 'Healthcare Provider',
                    appointment_type=appointment.get_appointment_type_display()
                )
                print(f'   ✅ Email sent: {result["recipient"]}')
            except Exception as e:
                print(f'   ❌ Failed to send email: {str(e)}')
        else:
            print(f'   ⚠️ No email address for patient')
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments (future, not cancelled/completed)."""
        upcoming_appointments = self.queryset.filter(
            appointment_datetime__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        )
        
        page = self.paginate_queryset(upcoming_appointments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(upcoming_appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment."""
        appointment = self.get_object()
        appointment.status = 'confirmed'
        appointment.save()
        
        # Use AppointmentListSerializer to include patient_name
        serializer = AppointmentListSerializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        
        # Use AppointmentListSerializer to include patient_name
        serializer = AppointmentListSerializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed."""
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        
        # Use AppointmentListSerializer to include patient_name
        serializer = AppointmentListSerializer(appointment)
        return Response(serializer.data)


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointment reminders.
    """
    queryset = AppointmentReminder.objects.all()
    serializer_class = AppointmentReminderSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'reminder_type', 'appointment']
    ordering_fields = ['reminder_datetime', 'created_at']
    ordering = ['reminder_datetime']
