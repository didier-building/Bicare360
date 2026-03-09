"""
Permission Classes for BiCare360 Chat System

This module defines custom permission classes that control access to
chat conversations and messages based on user roles and participation.

Permission Classes:
    - IsConversationParticipant: Restricts conversation access to participants only
    - IsMessageSenderOrRecipient: Restricts message access to conversation participants

Security Features:
    - Object-level permissions for fine-grained access control
    - Automatic participant verification
    - Support for all user types (Patient, Caregiver, Nurse)
    - Safe handling of anonymous users

Author: Didier IMANIRAHARI
Date: February 2026
"""

from rest_framework import permissions


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission class that allows access only to conversation participants.
    
    A user is considered a participant if they are:
    - The patient in the conversation
    - The caregiver in the conversation
    - The nurse in the conversation
    
    This permission is checked at the object level and applies to
    all HTTP methods (GET, POST, PUT, PATCH, DELETE).
    
    Usage:
        class ConversationViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsConversationParticipant]
    
    Examples:
        >>> # Patient accessing their conversation
        >>> request.user = patient_user
        >>> permission.has_object_permission(request, view, conversation)
        True
        
        >>> # Outsider trying to access conversation
        >>> request.user = other_user
        >>> permission.has_object_permission(request, view, conversation)
        False
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the requesting user is a participant in the conversation.
        
        Args:
            request: The HTTP request object with authenticated user
            view: The view handling the request
            obj: The Conversation object being accessed
        
        Returns:
            bool: True if user is a participant, False otherwise
        
        Note:
            This method is called after has_permission() and checks object-level
            permissions. It requires the user to be authenticated (handled by
            IsAuthenticated permission class).
        """
        # Anonymous users are never participants
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user is the patient in the conversation
        if obj.patient and hasattr(request.user, "patient"):
            if obj.patient.user == request.user:
                return True

        # Check if user is the caregiver in the conversation
        if obj.caregiver and hasattr(request.user, "caregiver_profile"):
            if obj.caregiver.user == request.user:
                return True

        # Check if user is the nurse in the conversation
        if obj.nurse and hasattr(request.user, "nurse_profile"):
            if obj.nurse.user == request.user:
                return True

        # User is not a participant
        return False


class IsMessageSenderOrRecipient(permissions.BasePermission):
    """
    Permission class that allows access to messages only for conversation participants.
    
    A user can access a message if they are a participant in the message's
    conversation (either as sender or recipient).
    
    This permission leverages the conversation's participant check to determine
    access rights. The actual message is accessible to all conversation participants,
    regardless of who sent it.
    
    Note:
        Deletion restrictions (only sender can delete) are enforced at the
        ViewSet level in the destroy() method, not in this permission class.
    
    Usage:
        class ChatMessageViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsMessageSenderOrRecipient]
    
    Examples:
        >>> # Sender accessing their message
        >>> request.user = sender_user
        >>> permission.has_object_permission(request, view, message)
        True
        
        >>> # Recipient accessing message
        >>> request.user = recipient_user
        >>> permission.has_object_permission(request, view, message)
        True
        
        >>> # Non-participant trying to access message
        >>> request.user = other_user
        >>> permission.has_object_permission(request, view, message)
        False
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the requesting user is a participant in the message's conversation.
        
        Args:
            request: The HTTP request object with authenticated user
            view: The view handling the request
            obj: The ChatMessage object being accessed
        
        Returns:
            bool: True if user is a conversation participant, False otherwise
        
        Implementation:
            This method delegates to IsConversationParticipant to check if the
            user has access to the parent conversation. If they're a participant
            in the conversation, they can access all messages in that conversation.
        """
        # Anonymous users are never participants
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user is a participant in the message's conversation
        conversation_permission = IsConversationParticipant()
        return conversation_permission.has_object_permission(
            request, view, obj.conversation
        )
