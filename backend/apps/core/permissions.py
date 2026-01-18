"""
Custom permission classes for BiCare360.

Implements role-based access control for different user types:
- Patients: Can only access their own data
- Providers: Can access assigned patient data
- Admins: Can access all data
"""

from rest_framework import permissions
from apps.patients.models import Patient

# Note: Provider model not yet implemented in enrollment app
# Keeping import commented for future use
# from apps.enrollment.models import Provider


class IsAuthenticatedUser(permissions.IsAuthenticated):
    """
    Allows access only to authenticated users.
    This is a pass-through that enforces authentication.
    """
    pass


class IsPatient(permissions.BasePermission):
    """
    Allows access only to users with Patient profile.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated and has a Patient profile."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'patient')


class IsProvider(permissions.BasePermission):
    """
    Allows access only to users with Provider profile.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated and has a Provider profile."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'provider')


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users (staff).
    """

    def has_permission(self, request, view):
        """Check if user is admin."""
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access only to object owner or admin users.
    
    For Patient objects: enrollment officer (enrolled_by) is the owner
    For appointments/messages: patient or provider owns the data
    """

    def has_object_permission(self, request, view, obj):
        """Check if user is owner or admin."""
        # Allow access to admins
        if request.user.is_staff:
            return True
        
        # For Patient model: check if user is the enrollment officer
        if isinstance(obj, Patient):
            # Patient.enrolled_by is the owner
            return obj.enrolled_by == request.user
        
        # For other models with patient FK: check if user is that patient
        if hasattr(obj, 'patient'):
            # In our current model, patients don't have a direct user relationship
            # This would need to be extended when patient-user relationship is established
            if hasattr(request.user, 'patient'):
                return obj.patient == request.user.patient
        
        # For other models with provider FK: check if user is that provider
        if hasattr(obj, 'provider'):
            if hasattr(request.user, 'provider'):
                return obj.provider == request.user.provider
        
        # For appointment/message objects: check if user is involved
        if hasattr(obj, 'recipient_patient'):
            if hasattr(request.user, 'patient'):
                return obj.recipient_patient == request.user.patient
        
        return False


class IsPatientOrAdmin(permissions.BasePermission):
    """
    Allows access to patients (their own data) or admins.
    """

    def has_permission(self, request, view):
        """Check permissions at view level."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow admins
        if request.user.is_staff:
            return True
        
        # Allow patients - check for patient attribute
        return hasattr(request.user, 'patient')

    def has_object_permission(self, request, view, obj):
        """Check permissions at object level."""
        # Allow admins
        if request.user.is_staff:
            return True
        
        # For Patient model: check if enrolled_by matches current user
        if isinstance(obj, Patient):
            return obj.enrolled_by == request.user
        
        # For models with patient FK: must be that patient
        if hasattr(obj, 'patient'):
            if hasattr(request.user, 'patient'):
                return obj.patient == request.user.patient
        
        # For models with recipient_patient FK: must be that patient
        if hasattr(obj, 'recipient_patient'):
            if hasattr(request.user, 'patient'):
                return obj.recipient_patient == request.user.patient
        
        return False


class IsProviderOrAdmin(permissions.BasePermission):
    """
    Allows access to providers (their patients' data) or admins.
    """

    def has_permission(self, request, view):
        """Check permissions at view level."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow admins
        if request.user.is_staff:
            return True
        
        # Allow providers
        return hasattr(request.user, 'provider')

    def has_object_permission(self, request, view, obj):
        """Check permissions at object level."""
        # Allow admins
        if request.user.is_staff:
            return True
        
        if not hasattr(request.user, 'provider'):
            return False
        
        provider = request.user.provider
        
        # For models with provider FK
        if hasattr(obj, 'provider'):
            return obj.provider == provider
        
        # For models with patient FK: check if provider treats this patient
        if hasattr(obj, 'patient'):
            # Check if this provider treats this patient
            return obj.patient.hospitals.filter(providers=provider).exists()
        
        return False
