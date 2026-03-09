"""
DRF Serializers for BiCare360 Chat System

This module defines Django REST Framework serializers for chat models,
handling serialization, deserialization, and validation of chat data.

Serializers:
    - ConversationSerializer: Conversation data with participant details
    - ChatMessageSerializer: Message data with sender information
    - MessageAttachmentSerializer: File attachment metadata

Features:
    - Nested serialization for related objects
    - Custom validation for business rules
    - Read-only fields for computed data
    - Optimized queries using select_related/prefetch_related

Author: Didier IMANIRAHARI
Date: February 2026
"""

from rest_framework import serializers

from apps.chat.models import ChatMessage, Conversation, MessageAttachment


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    
    Provides serialization/deserialization for conversations between
    patients, caregivers, and nurses.
    
    Fields:
        id (UUID): Read-only conversation identifier
        patient (int): Patient profile ID (optional)
        caregiver (int): Caregiver profile ID (optional)
        nurse (int): Nurse profile ID (optional)
        patient_name (str): Read-only patient full name
        caregiver_name (str): Read-only caregiver full name
        nurse_name (str): Read-only nurse full name
        unread_count (int): Read-only count of unread messages
        last_message (dict): Read-only last message summary
        created_at (datetime): Read-only conversation creation timestamp
        updated_at (datetime): Read-only last update timestamp
    
    Validation:
        - At least two participants required
        - Prevents duplicate conversations
    
    Examples:
        >>> # Serialize existing conversation
        >>> serializer = ConversationSerializer(conversation)
        >>> data = serializer.data
        
        >>> # Create new conversation
        >>> data = {"patient": 1, "caregiver": 2}
        >>> serializer = ConversationSerializer(data=data)
        >>> if serializer.is_valid():
        ...     conversation = serializer.save()
    """
    
    # Nested participant serializers (read-only for GET requests)
    patient = serializers.SerializerMethodField()
    caregiver = serializers.SerializerMethodField()
    nurse = serializers.SerializerMethodField()
    
    # Writable fields for POST/PUT (use IDs)
    patient_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, source='patient')
    caregiver_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, source='caregiver')
    nurse_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, source='nurse')
    
    # Computed fields
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            "id",
            "patient",
            "caregiver",
            "nurse",
            "patient_id",
            "caregiver_id",
            "nurse_id",
            "unread_count",
            "last_message",
            "message_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
    
    def get_patient(self, obj):
        """Get patient participant with user details."""
        if obj.patient and obj.patient.user:
            return {
                "id": obj.patient.id,
                "user": {
                    "id": obj.patient.user.id,
                    "email": obj.patient.user.email,
                    "first_name": obj.patient.user.first_name,
                    "last_name": obj.patient.user.last_name,
                    "get_full_name": obj.patient.user.get_full_name(),
                }
            }
        return None
    
    def get_caregiver(self, obj):
        """Get caregiver participant with user details."""
        if obj.caregiver and obj.caregiver.user:
            return {
                "id": obj.caregiver.id,
                "user": {
                    "id": obj.caregiver.user.id,
                    "email": obj.caregiver.user.email,
                    "first_name": obj.caregiver.user.first_name,
                    "last_name": obj.caregiver.user.last_name,
                    "get_full_name": obj.caregiver.user.get_full_name(),
                },
                "profession": obj.caregiver.profession,
            }
        return None
    
    def get_nurse(self, obj):
        """Get nurse participant with user details."""
        if obj.nurse and obj.nurse.user:
            return {
                "id": obj.nurse.id,
                "user": {
                    "id": obj.nurse.user.id,
                    "email": obj.nurse.user.email,
                    "first_name": obj.nurse.user.first_name,
                    "last_name": obj.nurse.user.last_name,
                    "get_full_name": obj.nurse.user.get_full_name(),
                },
                "specialization": obj.nurse.specialization,
            }
        return None
    
    def get_message_count(self, obj):
        """Get total message count."""
        return obj.messages.filter(is_deleted=False).count()
    
    def get_unread_count(self, obj):
        """
        Get count of unread messages in conversation.
        
        Args:
            obj (Conversation): Conversation instance
            
        Returns:
            int: Number of unread, non-deleted messages
        """
        # Get current user from request context
        request = self.context.get('request')
        if not request or not request.user:
            return 0
        
        # Count messages not sent by current user and not read
        return obj.messages.filter(
            is_deleted=False,
            is_read=False
        ).exclude(sender=request.user).count()
    
    def get_last_message(self, obj):
        """
        Get summary of last message in conversation.
        
        Args:
            obj (Conversation): Conversation instance
            
        Returns:
            dict: Last message data or None
        """
        last_msg = (
            obj.messages.filter(is_deleted=False)
            .order_by("-created_at")
            .select_related('sender')
            .first()
        )
        
        if last_msg:
            return {
                "id": str(last_msg.id),
                "conversation": str(last_msg.conversation_id),
                "sender": {
                    "id": last_msg.sender.id,
                    "email": last_msg.sender.email,
                    "first_name": last_msg.sender.first_name,
                    "last_name": last_msg.sender.last_name,
                    "get_full_name": last_msg.sender.get_full_name(),
                },
                "content": last_msg.content,
                "is_read": last_msg.is_read,
                "read_at": last_msg.read_at,
                "is_deleted": last_msg.is_deleted,
                "created_at": last_msg.created_at,
                "updated_at": last_msg.updated_at,
            }
        return None
    
    def validate(self, data):
        """
        Validate conversation data.
        
        Args:
            data (dict): Conversation data to validate
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        # Check for at least two participants
        participant_count = sum([
            data.get("patient") is not None,
            data.get("caregiver") is not None,
            data.get("nurse") is not None,
        ])
        
        if participant_count < 2:
            raise serializers.ValidationError(
                "A conversation must have at least two participants."
            )
        
        # Check for duplicate conversation (if creating new)
        if not self.instance:
            # Build filter kwargs for existing conversation
            filters = {}
            if data.get("patient"):
                filters["patient"] = data["patient"]
            if data.get("caregiver"):
                filters["caregiver"] = data["caregiver"]
            if data.get("nurse"):
                filters["nurse"] = data["nurse"]
            
            # Check if conversation already exists
            if Conversation.objects.filter(**filters).exists():
                raise serializers.ValidationError(
                    "A conversation already exists between these participants."
                )
        
        return data


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage model.
    
    Provides serialization/deserialization for chat messages with
    sender information and read status.
    
    Fields:
        id (UUID): Read-only message identifier
        conversation (UUID): Conversation this message belongs to
        sender (int): User who sent the message
        sender_name (str): Read-only sender full name
        content (str): Message content (max 5000 characters)
        is_read (bool): Read-only read status
        read_at (datetime): Read-only timestamp when message was read
        is_deleted (bool): Read-only soft delete flag
        created_at (datetime): Read-only message creation timestamp
        attachments (list): Read-only list of attachments
    
    Validation:
        - Content is required and non-empty
        - Content max length 5000 characters
    
    Examples:
        >>> # Create new message
        >>> data = {
        ...     "conversation": conversation_id,
        ...     "sender": user_id,
        ...     "content": "Hello, how are you?"
        ... }
        >>> serializer = ChatMessageSerializer(data=data)
        >>> if serializer.is_valid():
        ...     message = serializer.save()
    """
    
    # Nested sender object (read-only)
    sender = serializers.SerializerMethodField()
    
    # Computed fields
    attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "conversation",
            "sender",
            "content",
            "is_read",
            "read_at",
            "is_deleted",
            "created_at",
            "updated_at",
            "attachments",
        ]
        read_only_fields = [
            "id",
            "is_read",
            "read_at",
            "is_deleted",
            "created_at",
            "updated_at",
            "attachments",
        ]
    
    def get_sender(self, obj):
        """
        Get sender's full user data.
        
        Args:
            obj (ChatMessage): Message instance
            
        Returns:
            dict: Sender user data
        """
        return {
            "id": obj.sender.id,
            "email": obj.sender.email,
            "first_name": obj.sender.first_name,
            "last_name": obj.sender.last_name,
            "get_full_name": obj.sender.get_full_name(),
        }
    
    def get_attachments(self, obj):
        """
        Get list of message attachments.
        
        Args:
            obj (ChatMessage): Message instance
            
        Returns:
            list: List of attachment data dictionaries
        """
        return [
            {
                "id": str(attachment.id),
                "file_name": attachment.file_name,
                "file_size": attachment.file_size,
                "file_type": attachment.file_type,
                "file_url": attachment.file.url if attachment.file else None,
            }
            for attachment in obj.attachments.all()
        ]
    
    def validate_content(self, value):
        """
        Validate message content.
        
        Args:
            value (str): Message content
            
        Returns:
            str: Validated content
            
        Raises:
            ValidationError: If content is empty or invalid
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        
        if len(value) > 5000:
            raise serializers.ValidationError(
                "Message content cannot exceed 5000 characters."
            )
        
        return value.strip()


class MessageAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for MessageAttachment model.
    
    Provides serialization/deserialization for file attachments
    with validation for file type and size.
    
    Fields:
        id (UUID): Read-only attachment identifier
        message (UUID): Message this attachment belongs to
        file (File): Uploaded file
        file_name (str): Original filename
        file_size (int): File size in bytes
        file_type (str): MIME type
        uploaded_at (datetime): Read-only upload timestamp
        file_url (str): Read-only file URL
    
    Validation:
        - File type restrictions (images, PDFs, documents)
        - File size limit (10MB default)
    
    Note:
        Full file upload validation will be implemented with S3 setup.
    
    Examples:
        >>> # Serialize attachment
        >>> serializer = MessageAttachmentSerializer(attachment)
        >>> data = serializer.data
    """
    
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageAttachment
        fields = [
            "id",
            "message",
            "file",
            "file_name",
            "file_size",
            "file_type",
            "uploaded_at",
            "file_url",
        ]
        read_only_fields = [
            "id",
            "file_name",
            "file_size",
            "file_type",
            "uploaded_at",
            "file_url",
        ]
    
    def get_file_url(self, obj):
        """
        Get file URL.
        
        Args:
            obj (MessageAttachment): Attachment instance
            
        Returns:
            str: File URL or None
        """
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
