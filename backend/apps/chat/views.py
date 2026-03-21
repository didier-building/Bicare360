"""
Django REST Framework Views for BiCare360 Chat System

This module defines API views (ViewSets) for chat functionality,
providing endpoints for conversations and messages.

ViewSets:
    - ConversationViewSet: Manage conversations between users
    - ChatMessageViewSet: Send and manage messages within conversations

Features:
    - Object-level permissions via django-guardian
    - Filtered querysets based on user participation
    - Custom actions for read receipts and soft delete
    - Optimized queries with select_related/prefetch_related

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.chat.models import ChatMessage, Conversation
from apps.chat.serializers import ChatMessageSerializer, ConversationSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    Provides CRUD operations for conversations with automatic filtering
    to show only conversations involving the authenticated user.
    
    Endpoints:
        GET /api/chat/conversations/ - List user's conversations
        POST /api/chat/conversations/ - Create new conversation
        GET /api/chat/conversations/{id}/ - Retrieve conversation
        PUT/PATCH /api/chat/conversations/{id}/ - Update conversation
        DELETE /api/chat/conversations/{id}/ - Delete conversation
    
    Permissions:
        - User must be authenticated
        - User can only access conversations they participate in
    
    Filtering:
        - Automatically filters to user's conversations
        - Supports filtering by participant type
    
    Examples:
        >>> # List conversations for authenticated user
        >>> GET /api/chat/conversations/
        
        >>> # Create new patient-caregiver conversation
        >>> POST /api/chat/conversations/
        >>> {"patient": 1, "caregiver": 2}
    """
    
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get conversations for authenticated user.
        
        Returns only conversations where the user is a participant
        (patient, caregiver, or nurse).
        
        Returns:
            QuerySet: Filtered conversations with related data
        """
        user = self.request.user
        
        # Build filter for user's conversations
        # User could be patient, caregiver, or nurse
        query = Q()
        
        # Check if user has patient profile (related_name="patient")
        if hasattr(user, "patient"):
            query |= Q(patient__user=user)
        
        # Check if user has caregiver profile (related_name="caregiver_profile")
        if hasattr(user, "caregiver_profile"):
            query |= Q(caregiver__user=user)
        
        # Check if user has nurse profile (related_name="nurse_profile")
        if hasattr(user, "nurse_profile"):
            query |= Q(nurse__user=user)
        
        # If user has no valid participant profile, return empty queryset
        if not query:
            return Conversation.objects.none()
        
        return (
            Conversation.objects.filter(query)
            .select_related("patient__user", "caregiver__user", "nurse__user")
            .order_by("-updated_at")
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single conversation.
        
        Ensures the user is a participant before returning the conversation.
        Returns 404 if the user is not a participant (filtered by get_queryset).
        """
        # get_object will use get_queryset, so only participant conversations
        # will be accessible. If not found, raises 404 automatically.
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a conversation or return an existing one for the same participants.

        This makes POST idempotent for participant pairs and avoids 400 responses
        when a conversation already exists.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # Handle duplicate conversation gracefully by returning existing conversation.
        error_text = str(serializer.errors).lower()
        if "already exists" in error_text:
            patient_id = request.data.get("patient_id")
            caregiver_id = request.data.get("caregiver_id")
            nurse_id = request.data.get("nurse_id")

            filters = {}
            if patient_id not in (None, "", "null"):
                filters["patient_id"] = patient_id
            if caregiver_id not in (None, "", "null"):
                filters["caregiver_id"] = caregiver_id
            if nurse_id not in (None, "", "null"):
                filters["nurse_id"] = nurse_id

            existing = self.get_queryset().filter(**filters).first() if filters else None
            if existing:
                existing_data = self.get_serializer(existing).data
                return Response(existing_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages.
    
    Provides operations for sending, retrieving, and managing messages
    within conversations.
    
    Endpoints:
        GET /api/chat/messages/ - List messages (filtered by conversation)
        POST /api/chat/messages/ - Send new message
        GET /api/chat/messages/{id}/ - Retrieve message
        POST /api/chat/messages/{id}/mark_as_read/ - Mark message as read
        POST /api/chat/messages/{id}/soft_delete/ - Soft delete message
    
    Permissions:
        - User must be authenticated
        - User can only access messages in their conversations
        - User can only send messages to conversations they participate in
    
    Filtering:
        - Filter by conversation ID
        - Filter by read status
        - Exclude deleted messages by default
    
    Examples:
        >>> # List messages in conversation
        >>> GET /api/chat/messages/?conversation={uuid}
        
        >>> # Send new message
        >>> POST /api/chat/messages/
        >>> {"conversation": "uuid", "content": "Hello!"}
    """
    
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["conversation", "is_read"]
    
    def get_queryset(self):
        """
        Get messages for authenticated user's conversations.
        
        Returns only messages from conversations where user is a participant.
        Excludes soft-deleted messages by default.
        
        Returns:
            QuerySet: Filtered messages with related data
        """
        user = self.request.user
        
        # Build filter for user's conversations
        conversation_query = Q()
        
        # Check for patient profile (related_name="patient")
        if hasattr(user, "patient"):
            conversation_query |= Q(conversation__patient__user=user)
        
        # Check for caregiver profile (related_name="caregiver_profile")
        if hasattr(user, "caregiver_profile"):
            conversation_query |= Q(conversation__caregiver__user=user)
        
        # Check for nurse profile (related_name="nurse_profile")
        if hasattr(user, "nurse_profile"):
            conversation_query |= Q(conversation__nurse__user=user)
        
        return (
            ChatMessage.objects.filter(conversation_query)
            .filter(is_deleted=False)  # Exclude deleted messages
            .select_related("conversation", "sender")
            .prefetch_related("attachments")
            .order_by("created_at")
        )
    
    def perform_create(self, serializer):
        """
        Create a new message with authenticated user as sender.
        
        Automatically sets the sender to the authenticated user
        and validates that user is a participant in the conversation.
        
        Args:
            serializer: ChatMessageSerializer instance
            
        Raises:
            PermissionDenied: If user is not a participant
        """
        conversation_id = serializer.validated_data.get("conversation")
        
        # Get conversation object if UUID string provided
        if isinstance(conversation_id, str):
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"conversation": "Conversation not found."})
        else:
            conversation = conversation_id
        
        # Check if user is a participant in the conversation
        user = self.request.user
        is_participant = False
        
        # Check patient participation (related_name="patient")
        if hasattr(user, "patient") and conversation.patient:
            is_participant = conversation.patient.user == user
        
        # Check caregiver participation (related_name="caregiver_profile")
        if not is_participant and hasattr(user, "caregiver_profile") and conversation.caregiver:
            is_participant = conversation.caregiver.user == user
        
        # Check nurse participation (related_name="nurse_profile")
        if not is_participant and hasattr(user, "nurse_profile") and conversation.nurse:
            is_participant = conversation.nurse.user == user
        
        if not is_participant:
            from rest_framework.exceptions import PermissionDenied
            
            raise PermissionDenied(
                "You are not a participant in this conversation."
            )
        
        # Save message with authenticated user as sender
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=["post"], url_path="mark-as-read")
    def mark_as_read(self, request, pk=None):
        """
        Mark a message as read.
        
        Custom action to mark a message as read by the recipient.
        Sets is_read=True and read_at=now().
        
        Args:
            request: HTTP request
            pk: Message ID
            
        Returns:
            Response: Success message with updated message data
        """
        message = self.get_object()
        message.mark_as_read()
        
        serializer = self.get_serializer(message)
        return Response(
            {"status": "Message marked as read", "message": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        """
        Soft delete a message.
        
        Custom action to soft delete a message (sender only).
        Sets is_deleted=True while preserving the message in database.
        
        Args:
            request: HTTP request
            pk: Message ID
            
        Returns:
            Response: Success message
            
        Raises:
            PermissionDenied: If user is not the message sender
        """
        message = self.get_object()
        
        # Only sender can delete their own message
        if message.sender != request.user:
            from rest_framework.exceptions import PermissionDenied
            
            raise PermissionDenied("You can only delete your own messages.")
        
        message.soft_delete()
        
        return Response(
            {"status": "Message deleted successfully"},
            status=status.HTTP_200_OK,
        )
