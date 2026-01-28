"""Views for Caregiver app."""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from apps.core.permissions import IsAuthenticatedUser
from apps.caregivers.models import Caregiver, CaregiverBooking, CaregiverReview
from apps.caregivers.serializers import (
    CaregiverListSerializer, CaregiverDetailSerializer,
    CaregiverBookingSerializer, CaregiverReviewSerializer
)


class CaregiverViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for browsing caregivers."""
    queryset = Caregiver.objects.filter(is_active=True).prefetch_related('services', 'certifications')
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['profession', 'province', 'district', 'availability_status', 'is_verified']
    search_fields = ['first_name', 'last_name', 'bio', 'services__service_name']
    ordering_fields = ['rating', 'hourly_rate', 'experience_years', 'created_at']
    ordering = ['-rating', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CaregiverDetailSerializer
        return CaregiverListSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available caregivers."""
        caregivers = self.queryset.filter(availability_status='available')
        page = self.paginate_queryset(caregivers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(caregivers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Get top-rated caregivers."""
        caregivers = self.queryset.filter(rating__gte=4.5).order_by('-rating', '-total_reviews')[:10]
        serializer = self.get_serializer(caregivers, many=True)
        return Response(serializer.data)


class CaregiverBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing caregiver bookings."""
    queryset = CaregiverBooking.objects.all().select_related('patient', 'caregiver')
    serializer_class = CaregiverBookingSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'caregiver', 'patient']
    ordering_fields = ['start_datetime', 'created_at']
    ordering = ['-start_datetime']
    
    def get_queryset(self):
        """Filter bookings based on user."""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'patient'):
            return queryset.filter(patient=self.request.user.patient)
        elif hasattr(self.request.user, 'caregiver_profile'):
            return queryset.filter(caregiver=self.request.user.caregiver_profile)
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign patient if authenticated."""
        if hasattr(self.request.user, 'patient'):
            serializer.save(patient=self.request.user.patient)
        else:
            serializer.save()
    
    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        """Confirm a booking (caregiver action)."""
        booking = self.get_object()
        booking.status = 'confirmed'
        booking.save()
        return Response(self.get_serializer(booking).data)
    
    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.cancellation_reason = request.data.get('reason', '')
        booking.cancelled_by = 'patient' if hasattr(request.user, 'patient') else 'caregiver'
        booking.save()
        return Response(self.get_serializer(booking).data)
    
    @action(detail=True, methods=['patch'])
    def complete(self, request, pk=None):
        """Mark booking as completed."""
        booking = self.get_object()
        booking.status = 'completed'
        booking.save()
        return Response(self.get_serializer(booking).data)


class CaregiverReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for caregiver reviews."""
    queryset = CaregiverReview.objects.all().select_related('patient', 'caregiver', 'booking')
    serializer_class = CaregiverReviewSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['caregiver', 'rating']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Create review and update caregiver rating."""
        review = serializer.save(
            patient=self.request.user.patient,
            caregiver=serializer.validated_data['booking'].caregiver
        )
        
        # Update caregiver rating
        caregiver = review.caregiver
        avg_rating = caregiver.reviews.aggregate(Avg('rating'))['rating__avg']
        caregiver.rating = round(avg_rating, 2)
        caregiver.total_reviews = caregiver.reviews.count()
        caregiver.save()
