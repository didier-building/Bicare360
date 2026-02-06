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
    
    # Read-only computed fields
    patient_name = serializers.SerializerMethodField()
    caregiver_name = serializers.SerializerMethodField()
    nurse_name = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            "id",
            "patient",
            "caregiver",
            "nurse",
            "patient_name",
            "caregiver_name",
            "nurse_name",
            "unread_count",
            "last_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "patient_name",
            "caregiver_name",
            "nurse_name",
            "unread_count",
            "last_message",
        ]
    
    def get_patient_name(self, obj):
        """
        Get patient's full name.
        
        Args:
            obj (Conversation): Conversation instance
            
        Returns:
            str: Patient full name or None
        """
        if obj.patient and obj.patient.user:
            return obj.patient.user.get_full_name()
        return None
    
    def get_caregiver_name(self, obj):
        """
        Get caregiver's full name.
        
        Args:
            obj (Conversation): Conversation instance
            
        Returns:
            str: Caregiver full name or None
        """
        if obj.caregiver and obj.caregiver.user:
            return obj.caregiver.user.get_full_name()
        return None
    
    def get_nurse_name(self, obj):
        """
        Get nurse's full name.
        
        Args:
            obj (Conversation): Conversation instance
            
        Returns:
            str: Nurse full name or None
        """
        if obj.nurse and obj.nurse.user:
            return obj.nurse.user.get_full_name()
        return None
    
    def get_unread_count(self, obj):
        """
        Get count of unread messages in conversation.
        
        Args:
            obj (Conversation): Conversation instance
            
        Returns:
            int: Number of unread, non-deleted messages
        """
        return obj.messages.filter(is_read=False, is_deleted=False).count()
    
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
            .first()
        )
        
        if last_msg:
            return {
                "content": last_msg.content[:50] + "..." if len(last_msg.content) > 50 else last_msg.content,
                "sender_name": last_msg.sender.get_full_name(),
                "created_at": last_msg.created_at,
                "is_read": last_msg.is_read,
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
    
    # Read-only computed fields
    sender_name = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_name",
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
            "sender",  # Sender is set automatically from request.user
            "is_read",
            "read_at",
            "is_deleted",
            "created_at",
            "updated_at",
            "sender_name",
            "attachments",
        ]
    
    def get_sender_name(self, obj):
        """
        Get sender's full name.
        
        Args:
            obj (ChatMessage): Message instance
            
        Returns:
            str: Sender full name
        """
        return obj.sender.get_full_name()
    
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
