"""Views for Caregiver app."""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta
from apps.core.permissions import IsAuthenticatedUser
from apps.caregivers.models import Caregiver, CaregiverBooking, CaregiverReview
from apps.caregivers.serializers import (
    CaregiverListSerializer, CaregiverDetailSerializer,
    CaregiverBookingSerializer, CaregiverReviewSerializer,
    CaregiverAuthSerializer
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


@api_view(['POST'])
@permission_classes([AllowAny])
def caregiver_login(request):
    """
    Caregiver portal login endpoint.
    POST /api/v1/caregivers/login/
    
    Authenticates caregiver using email and password.
    Returns JWT tokens and caregiver information.
    
    Request body:
    {
        "email": "caregiver@example.com",
        "password": "password123"
    }
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Both email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find caregiver by email
    try:
        caregiver = Caregiver.objects.select_related('user').get(email=email)
    except Caregiver.DoesNotExist:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if caregiver has a user account
    if not caregiver.user:
        return Response({
            'error': 'No user account linked to this caregiver profile'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Authenticate user
    user = authenticate(username=caregiver.user.username, password=password)
    if not user:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if caregiver is active
    if not caregiver.is_active:
        return Response({
            'error': 'Caregiver account is inactive. Please contact support.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['role'] = 'caregiver'
    refresh['caregiver_id'] = str(caregiver.id)
    
    serializer = CaregiverAuthSerializer(caregiver)
    
    return Response({
        'message': 'Login successful',
        'caregiver': serializer.data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': 'caregiver'
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def caregiver_dashboard_stats(request):
    """
    Get dashboard statistics for logged-in caregiver.
    GET /api/v1/caregivers/dashboard-stats/
    
    Returns:
    - Total bookings
    - Upcoming bookings
    - Completed bookings
    - Total earnings
    - Average rating
    - Recent reviews
    """
    # Get caregiver profile
    try:
        caregiver = request.user.caregiver_profile
    except Caregiver.DoesNotExist:
        return Response({
            'error': 'No caregiver profile found for this user'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Calculate stats
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    bookings = CaregiverBooking.objects.filter(caregiver=caregiver)
    
    stats = {
        'total_bookings': bookings.count(),
        'pending_bookings': bookings.filter(status='pending').count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'upcoming_bookings': bookings.filter(
            status__in=['pending', 'confirmed'],
            start_datetime__gte=now
        ).count(),
        'completed_bookings': bookings.filter(status='completed').count(),
        'cancelled_bookings': bookings.filter(status='cancelled').count(),
        'total_earnings': float(bookings.filter(status='completed').aggregate(
            total=Count('total_cost')
        )['total'] or 0),
        'this_week_earnings': float(bookings.filter(
            status='completed',
            created_at__gte=week_ago
        ).aggregate(total=Count('total_cost'))['total'] or 0),
        'this_month_earnings': float(bookings.filter(
            status='completed',
            created_at__gte=month_ago
        ).aggregate(total=Count('total_cost'))['total'] or 0),
        'rating': float(caregiver.rating),
        'total_reviews': caregiver.total_reviews,
        'availability_status': caregiver.availability_status,
        'is_verified': caregiver.is_verified,
    }
    
    # Get upcoming bookings
    upcoming = bookings.filter(
        status__in=['pending', 'confirmed'],
        start_datetime__gte=now
    ).order_by('start_datetime')[:5]
    
    stats['upcoming_bookings_list'] = CaregiverBookingSerializer(upcoming, many=True).data
    
    # Get recent reviews
    recent_reviews = caregiver.reviews.all()[:5]
    stats['recent_reviews'] = CaregiverReviewSerializer(recent_reviews, many=True).data
    
    return Response(stats, status=status.HTTP_200_OK)
