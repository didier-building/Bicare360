"""
Views for Patient app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsAuthenticatedUser
from apps.patients.models import Patient, Address, EmergencyContact
from apps.patients.serializers import (
    PatientListSerializer,
    PatientDetailSerializer,
    PatientCreateSerializer,
    PatientRegistrationSerializer,
    AddressSerializer,
    EmergencyContactSerializer,
)
from apps.appointments.models import Appointment
from apps.enrollment.models import Hospital


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patients.
    
    Provides CRUD operations for patients with filtering, search, and ordering.
    """

    queryset = Patient.objects.select_related("enrolled_by", "address").prefetch_related(
        "emergency_contacts"
    )
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "gender", "language_preference", "enrolled_by"]
    search_fields = [
        "first_name",
        "last_name",
        "national_id",
        "phone_number",
        "email",
    ]
    ordering_fields = ["enrolled_date", "last_name", "date_of_birth"]
    ordering = ["-enrolled_date"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return PatientListSerializer
        elif self.action == "create":
            return PatientCreateSerializer
        return PatientDetailSerializer

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        """Get or update current patient's data based on JWT token."""
        try:
            patient = request.user.patient
        except Patient.DoesNotExist:
            return Response({
                'error': 'Patient profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            serializer = PatientDetailSerializer(patient)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = PatientDetailSerializer(
                patient, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Change password for the current authenticated user."""
        try:
            patient = request.user.patient
        except Patient.DoesNotExist:
            return Response({
                'error': 'Patient profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'detail': 'Both current_password and new_password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not request.user.check_password(current_password):
            return Response({
                'detail': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'detail': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a patient (soft delete)."""
        patient = self.get_object()
        patient.is_active = False
        patient.save()
        return Response(
            {"status": "Patient deactivated successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Reactivate a patient."""
        patient = self.get_object()
        patient.is_active = True
        patient.save()
        return Response(
            {"status": "Patient activated successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Advanced patient search with full-text search and filtering.
        Supports:
        - Full-text search: ?q=search_term
        - Filters: ?is_active=true, ?gender=M, ?blood_type=O+
        - Sorting: ?sort=name&order=asc
        - Pagination: ?limit=10
        """
        from django.db.models import Q
        from django.utils.dateparse import parse_date
        
        queryset = self.get_queryset()
        
        # Full-text search
        search_query = request.query_params.get('q', '').strip()
        if search_query:
            # Split query into parts for multi-word search
            query_parts = search_query.split()
            search_filter = Q()
            
            for part in query_parts:
                # Each part must match at least one field (OR within fields)
                part_filter = Q(
                    Q(first_name__icontains=part) |
                    Q(last_name__icontains=part) |
                    Q(first_name_kinyarwanda__icontains=part) |
                    Q(last_name_kinyarwanda__icontains=part) |
                    Q(email__icontains=part) |
                    Q(phone_number__icontains=part) |
                    Q(national_id__icontains=part)
                )
                search_filter &= part_filter  # AND between parts
            
            queryset = queryset.filter(search_filter)
            # When searching, include both active and inactive patients
        else:
            # When not searching, default to active patients only
            queryset = queryset.filter(is_active=True)
        
        # Filter by active status (explicit parameter overrides defaults)
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter by gender
        gender = request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by blood type
        blood_type = request.query_params.get('blood_type')
        if blood_type:
            queryset = queryset.filter(blood_type=blood_type)
        
        # Filter by enrollment date range
        enrolled_after = request.query_params.get('enrolled_after')
        if enrolled_after:
            try:
                enrolled_after_date = parse_date(enrolled_after)
                queryset = queryset.filter(enrolled_date__date__gte=enrolled_after_date)
            except (ValueError, TypeError):
                pass
        
        enrolled_before = request.query_params.get('enrolled_before')
        if enrolled_before:
            try:
                enrolled_before_date = parse_date(enrolled_before)
                queryset = queryset.filter(enrolled_date__date__lte=enrolled_before_date)
            except (ValueError, TypeError):
                pass
        
        # Sorting
        sort_field = request.query_params.get('sort', 'enrolled_date')
        sort_order = request.query_params.get('order', 'desc')
        
        if sort_field == 'name':
            # Sort by first_name then last_name
            if sort_order == 'asc':
                queryset = queryset.order_by('first_name', 'last_name')
            else:
                queryset = queryset.order_by('-first_name', '-last_name')
        elif sort_field == 'age':
            # Older people first (oldest date of birth)
            if sort_order == 'asc':
                queryset = queryset.order_by('-date_of_birth')  # Oldest first
            else:
                queryset = queryset.order_by('date_of_birth')   # Youngest first
        else:
            # Default: enrolled_date
            if sort_order == 'asc':
                queryset = queryset.order_by(sort_field)
            else:
                queryset = queryset.order_by(f'-{sort_field}')
        
        # Limit results
        limit = request.query_params.get('limit')
        if limit:
            try:
                limit_int = int(limit)
                queryset = queryset[:limit_int]
            except (ValueError, TypeError):
                pass
        
        # Use list serializer
        serializer = PatientListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get patient statistics."""
        from django.utils import timezone
        from datetime import timedelta
        
        total = Patient.objects.count()
        active = Patient.objects.filter(is_active=True).count()
        inactive = total - active
        
        # Enrollment stats
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        new_enrollments_today = Patient.objects.filter(
            enrolled_date__date=today
        ).count()
        
        new_enrollments_this_week = Patient.objects.filter(
            enrolled_date__date__gte=week_ago
        ).count()
        
        by_gender = {}
        for gender, _ in Patient.GENDER_CHOICES:
            by_gender[gender] = Patient.objects.filter(gender=gender).count()

        return Response({
            "total_patients": total,
            "active_patients": active,
            "inactive_patients": inactive,
            "new_enrollments_today": new_enrollments_today,
            "new_enrollments_this_week": new_enrollments_this_week,
            "by_gender": by_gender,
        })
    
    @action(detail=True, methods=["get"])
    def export_data(self, request, pk=None):
        """
        Export all patient data (GDPR right to data portability).
        GET /api/v1/patients/{id}/export-data/
        """
        patient = self.get_object()
        
        # Collect all patient-related data
        from apps.consents.serializers import ConsentSerializer, PrivacyPreferenceSerializer
        
        data = {
            'patient': PatientDetailSerializer(patient).data,
            'consents': ConsentSerializer(patient.consents.all(), many=True).data,
            'privacy_preferences': None,
            'appointments': [],
            'prescriptions': [],
            'discharge_summaries': [],
        }
        
        # Add privacy preferences if they exist
        if hasattr(patient, 'privacy_preference'):
            data['privacy_preferences'] = PrivacyPreferenceSerializer(patient.privacy_preference).data
        
        # Add appointments if any
        if hasattr(patient, 'appointments'):
            from apps.appointments.serializers import AppointmentSerializer
            data['appointments'] = AppointmentSerializer(patient.appointments.all(), many=True).data
        
        return Response(data)
    
    @action(detail=True, methods=["post"])
    def request_deletion(self, request, pk=None):
        """
        Request patient data deletion (GDPR right to be forgotten).
        POST /api/v1/patients/{id}/request-deletion/
        
        In production, this should trigger a review process rather than immediate deletion.
        """
        patient = self.get_object()
        
        # In production: Create a deletion request ticket and notify administrators
        # For now, we'll just mark the patient as inactive and log the request
        
        patient.is_active = False
        patient.save()
        
        # Log the deletion request in consent audit logs if consent exists
        from apps.consents.models import ConsentAuditLog
        consents = patient.consents.all()
        for consent in consents:
            ConsentAuditLog.objects.create(
                consent=consent,
                action='exported',
                performed_by='patient',
                details='Data deletion requested by patient (GDPR right to erasure)'
            )
        
        return Response({
            'message': 'Data deletion request submitted successfully',
            'detail': 'Your request is being processed. You will be notified once completed.',
            'patient_id': patient.id,
            'status': 'pending_review'
        })


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing patient addresses."""

    queryset = Address.objects.select_related("patient")
    serializer_class = AddressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["province", "district", "sector"]


class EmergencyContactViewSet(viewsets.ModelViewSet):
    """ViewSet for managing emergency contacts."""

    queryset = EmergencyContact.objects.select_related("patient")
    serializer_class = EmergencyContactSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["patient", "relationship", "is_primary"]


@api_view(['POST'])
@permission_classes([AllowAny])
def patient_register(request):
    """
    Patient self-registration endpoint.
    POST /api/patients/register/
    
    Creates a new User and Patient account for patient portal access.
    Returns JWT tokens for immediate login after registration.
    """
    serializer = PatientRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        patient = serializer.save()
        
        # Generate JWT tokens for immediate login
        refresh = RefreshToken.for_user(patient.user)
        
        return Response({
            'message': 'Registration successful',
            'patient': {
                'id': patient.id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'email': patient.email,
                'phone_number': patient.phone_number,
                'national_id': patient.national_id,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def patient_login(request):
    """
    Patient portal login endpoint.
    POST /api/patients/login/
    
    Authenticates patient using username (or national_id) and password.
    Returns JWT tokens and patient information.
    
    Request body:
    {
        "username": "patient_username or national_id",
        "password": "patient_password"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Both username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Try authentication with username first
    user = authenticate(username=username, password=password)
    
    # If username auth fails, try to find patient by national_id and get their username
    if not user:
        try:
            patient = Patient.objects.select_related('user').get(national_id=username)
            if patient.user:
                user = authenticate(username=patient.user.username, password=password)
        except Patient.DoesNotExist:
            pass
    
    if not user:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user has an associated patient account
    try:
        patient = user.patient
    except Patient.DoesNotExist:
        return Response({
            'error': 'No patient account found for this user'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if patient is active
    if not patient.is_active:
        return Response({
            'error': 'Patient account is inactive. Please contact support.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'patient': {
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'email': patient.email,
            'phone_number': patient.phone_number,
            'national_id': patient.national_id,
            'date_of_birth': patient.date_of_birth,
            'gender': patient.gender,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_appointment(request):
    """
    Allow authenticated patient to request an appointment.
    Patient must be linked to a User account.
    """
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        return Response({
            'error': 'You are not registered as a patient'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate required fields
    required_fields = ['hospital_id', 'appointment_type', 'appointment_datetime', 'reason']
    missing_fields = [field for field in required_fields if field not in request.data]
    
    if missing_fields:
        return Response({
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        hospital = Hospital.objects.get(id=request.data.get('hospital_id'))
    except Hospital.DoesNotExist:
        return Response({
            'error': 'Hospital not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create appointment with status 'scheduled' (pending nurse confirmation)
    appointment = Appointment.objects.create(
        patient=patient,
        hospital=hospital,
        appointment_datetime=request.data.get('appointment_datetime'),
        appointment_type=request.data.get('appointment_type'),
        status='scheduled',  # Patient requested, pending nurse confirmation
        location_type=request.data.get('location_type', 'hospital'),
        reason=request.data.get('reason'),
        notes=request.data.get('notes', ''),
        provider_name=request.data.get('provider_name', 'Healthcare Provider'),
        department=request.data.get('department', ''),
    )
    
    return Response({
        'message': 'Appointment request submitted successfully',
        'appointment': {
            'id': appointment.id,
            'hospital': hospital.name,
            'appointment_type': appointment.get_appointment_type_display(),
            'appointment_datetime': appointment.appointment_datetime.isoformat(),
            'status': appointment.status,
            'reason': appointment.reason,
        }
    }, status=status.HTTP_201_CREATED)
