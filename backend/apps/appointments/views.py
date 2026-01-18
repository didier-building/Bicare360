"""
Views for appointments app.
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
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
from apps.core.permissions import IsAuthenticatedUser


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments.
    Provides CRUD operations and custom actions.
    """
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'patient', 'hospital', 'location_type']
    search_fields = ['patient__first_name', 'patient__last_name', 'provider_name', 'reason']
    ordering_fields = ['appointment_datetime', 'created_at']
    ordering = ['appointment_datetime']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'list':
            return AppointmentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AppointmentCreateSerializer
        elif self.action == 'retrieve':
            return AppointmentDetailSerializer
        return AppointmentSerializer
    
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
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark appointment as completed."""
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
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
