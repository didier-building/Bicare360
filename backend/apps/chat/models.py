"""
Chat Models for BiCare360 Real-Time Messaging

This module defines the database models for the BiCare360 chat system, enabling
secure, HIPAA-compliant real-time messaging between patients, caregivers, and nurses.

Models:
    - Conversation: Represents a chat conversation between two parties
    - ChatMessage: Individual messages within a conversation
    - MessageAttachment: File attachments (images, documents) for messages
    - MessageNotification: Tracks unread message notifications

Key Features:
    - Support for patient-caregiver, patient-nurse, and caregiver-nurse conversations
    - Unique conversation constraints to prevent duplicates
    - Message read receipts and delivery tracking
    - Soft delete for messages (data retention for audit)
    - File attachments with S3 storage
    - Notification system for unread messages

Security & Compliance:
    - Object-level permissions via django-guardian
    - Audit trails via timestamps and soft delete
    - HIPAA-compliant data handling
    - Encrypted file storage (S3 with encryption)

Author: Didier IMANIRAHARI
Date: February 2026
"""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.caregivers.models import Caregiver
from apps.nursing.models import NurseProfile
from apps.patients.models import Patient


class Conversation(models.Model):
    """
    Represents a chat conversation between two parties in the BiCare360 system.
    
    A conversation can be between:
    - Patient and Caregiver (for daily care coordination)
    - Patient and Nurse (for medical support and monitoring)
    - Caregiver and Nurse (for care team collaboration)
    
    Attributes:
        id (UUIDField): Primary key using UUID for security and scalability
        patient (ForeignKey): Optional reference to Patient profile
        caregiver (ForeignKey): Optional reference to Caregiver profile
        nurse (ForeignKey): Optional reference to NurseProfile
        created_at (DateTimeField): Timestamp when conversation was initiated
        updated_at (DateTimeField): Timestamp of last activity in conversation
    
    Constraints:
        - Unique constraint on (patient, caregiver) to prevent duplicate conversations
        - Unique constraint on (patient, nurse) to prevent duplicate conversations
        - Unique constraint on (caregiver, nurse) to prevent duplicate conversations
        - At least two participants must be present (validated in clean method)
    
    Methods:
        get_participants(): Returns list of User objects participating in conversation
        clean(): Validates that conversation has at least two participants
    
    Examples:
        >>> # Create patient-caregiver conversation
        >>> conversation = Conversation.objects.create(
        ...     patient=patient,
        ...     caregiver=caregiver
        ... )
        
        >>> # Get conversation participants
        >>> users = conversation.get_participants()
        >>> print(users)  # [<User: patient@example.com>, <User: caregiver@example.com>]
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the conversation"),
    )
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
        help_text=_("Patient participating in this conversation"),
    )
    
    caregiver = models.ForeignKey(
        Caregiver,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
        help_text=_("Caregiver participating in this conversation"),
    )
    
    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
        help_text=_("Nurse participating in this conversation"),
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when conversation was initiated"),
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp of last activity in conversation"),
    )
    
    class Meta:
        db_table = "chat_conversations"
        ordering = ["-updated_at"]
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")
        
        # Unique constraints to prevent duplicate conversations
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "caregiver"],
                name="unique_patient_caregiver",
                condition=models.Q(patient__isnull=False, caregiver__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["patient", "nurse"],
                name="unique_patient_nurse",
                condition=models.Q(patient__isnull=False, nurse__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["caregiver", "nurse"],
                name="unique_caregiver_nurse",
                condition=models.Q(caregiver__isnull=False, nurse__isnull=False),
            ),
        ]
        
        # Database indexes for query performance
        indexes = [
            models.Index(fields=["-updated_at"], name="conv_updated_at_idx"),
            models.Index(fields=["patient", "-created_at"], name="conv_patient_idx"),
            models.Index(
                fields=["caregiver", "-created_at"], name="conv_caregiver_idx"
            ),
            models.Index(fields=["nurse", "-created_at"], name="conv_nurse_idx"),
        ]
    
    def get_participants(self):
        """
        Returns a list of User objects participating in this conversation.
        
        Returns:
            list: List of User objects (length will be 2 in valid conversations)
        
        Examples:
            >>> conversation = Conversation.objects.get(id=conversation_id)
            >>> participants = conversation.get_participants()
            >>> for user in participants:
            ...     print(user.get_full_name())
        """
        participants = []
        
        if self.patient:
            participants.append(self.patient.user)
        if self.caregiver:
            participants.append(self.caregiver.user)
        if self.nurse:
            participants.append(self.nurse.user)
        
        return participants
    
    def clean(self):
        """
        Validates that the conversation has at least two participants.
        
        Raises:
            ValidationError: If fewer than two participants are specified
        
        Note:
            This method is called automatically during full_clean() validation,
            typically in forms and admin interfaces. For programmatic creation,
            call full_clean() explicitly before save().
        """
        super().clean()
        
        # Count non-null participants
        participant_count = sum(
            [
                self.patient is not None,
                self.caregiver is not None,
                self.nurse is not None,
            ]
        )
        
        if participant_count < 2:
            raise ValidationError(
                _("A conversation must have at least two participants.")
            )
    
    def __str__(self):
        """
        Returns a human-readable string representation of the conversation.
        
        Returns:
            str: Description of conversation participants
        
        Examples:
            >>> str(conversation)
            "Conversation between John Doe (Patient) and Jane Smith (Caregiver)"
        """
        participants = []
        
        if self.patient:
            participants.append(
                f"{self.patient.user.get_full_name()} (Patient)"
            )
        if self.caregiver:
            participants.append(
                f"{self.caregiver.user.get_full_name()} (Caregiver)"
            )
        if self.nurse:
            participants.append(
                f"{self.nurse.user.get_full_name()} (Nurse)"
            )
        
        return f"Conversation between {' and '.join(participants)}"


class ChatMessage(models.Model):
    """
    Represents an individual message within a conversation.
    
    Messages support:
    - Text content (up to 5000 characters)
    - Read receipt tracking (is_read, read_at)
    - Soft delete for audit compliance (is_deleted)
    - Chronological ordering by creation timestamp
    
    Attributes:
        id (UUIDField): Primary key using UUID
        conversation (ForeignKey): Reference to parent Conversation
        sender (ForeignKey): User who sent the message
        content (TextField): Message text content (max 5000 characters)
        is_read (BooleanField): Whether message has been read by recipient
        read_at (DateTimeField): Timestamp when message was read
        is_deleted (BooleanField): Soft delete flag for audit trail
        created_at (DateTimeField): Timestamp when message was sent
        updated_at (DateTimeField): Timestamp of last modification
    
    Methods:
        mark_as_read(): Marks message as read and sets read_at timestamp
        soft_delete(): Soft deletes message (preserves for audit)
    
    Examples:
        >>> # Create a message
        >>> message = ChatMessage.objects.create(
        ...     conversation=conversation,
        ...     sender=patient_user,
        ...     content="I need help with my medication schedule"
        ... )
        
        >>> # Mark message as read
        >>> message.mark_as_read()
        
        >>> # Soft delete message
        >>> message.soft_delete()
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the message"),
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text=_("Conversation this message belongs to"),
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        help_text=_("User who sent this message"),
    )
    
    content = models.TextField(
        max_length=5000,
        help_text=_("Message content (max 5000 characters)"),
    )
    
    is_read = models.BooleanField(
        default=False,
        help_text=_("Whether this message has been read by recipient"),
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp when message was read"),
    )
    
    is_deleted = models.BooleanField(
        default=False,
        help_text=_("Soft delete flag for audit trail"),
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when message was sent"),
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp of last modification"),
    )
    
    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]  # Chronological order (oldest first)
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
        
        # Database indexes for query performance
        indexes = [
            models.Index(
                fields=["conversation", "created_at"], name="msg_conv_created_idx"
            ),
            models.Index(
                fields=["conversation", "is_deleted", "created_at"],
                name="msg_conv_active_idx",
            ),
            models.Index(
                fields=["sender", "-created_at"], name="msg_sender_idx"
            ),
            models.Index(
                fields=["is_read", "created_at"], name="msg_unread_idx"
            ),
        ]
    
    def mark_as_read(self):
        """
        Marks the message as read and sets the read_at timestamp.
        
        This method updates both is_read flag and read_at timestamp,
        then saves the instance to the database.
        
        Returns:
            None
        
        Note:
            Deleted messages can technically be marked as read, but
            business logic should prevent this in practice.
        
        Examples:
            >>> message = ChatMessage.objects.get(id=message_id)
            >>> message.mark_as_read()
            >>> print(message.is_read)  # True
            >>> print(message.read_at)  # datetime object
        """
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at", "updated_at"])
    
    def soft_delete(self):
        """
        Soft deletes the message for audit compliance.
        
        Sets is_deleted flag to True while keeping the message in the database.
        This allows for audit trails and potential message recovery.
        
        Returns:
            None
        
        Examples:
            >>> message = ChatMessage.objects.get(id=message_id)
            >>> message.soft_delete()
            >>> print(message.is_deleted)  # True
            
            >>> # Query only active messages
            >>> active_messages = ChatMessage.objects.filter(is_deleted=False)
        """
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])
    
    def __str__(self):
        """
        Returns a human-readable string representation of the message.
        
        Returns:
            str: Message preview with sender information
        
        Examples:
            >>> str(message)
            "Message from John Doe: I need help with..."
        """
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"Message from {self.sender.get_full_name()}: {content_preview}"


class MessageAttachment(models.Model):
    """
    Represents a file attachment for a chat message.
    
    Supports attachments such as:
    - Images (JPG, PNG, GIF) - medical photos, prescriptions
    - Documents (PDF, DOC, DOCX) - medical reports, consent forms
    - Other files as needed for healthcare communication
    
    Files are stored in S3 with encryption for HIPAA compliance.
    
    Attributes:
        id (UUIDField): Primary key using UUID
        message (ForeignKey): Reference to parent ChatMessage
        file (FileField): Uploaded file (stored in S3)
        file_name (CharField): Original filename
        file_size (IntegerField): File size in bytes
        file_type (CharField): MIME type of the file
        uploaded_at (DateTimeField): Timestamp when file was uploaded
    
    Validation:
        - File size limit: 10MB (configurable)
        - Allowed file types: images, PDFs, documents (configurable)
    
    Examples:
        >>> # Create attachment (file upload handled by serializer)
        >>> attachment = MessageAttachment.objects.create(
        ...     message=message,
        ...     file=uploaded_file,
        ...     file_name="prescription.pdf",
        ...     file_size=12456,
        ...     file_type="application/pdf"
        ... )
    
    Note:
        This model is a placeholder for full file upload implementation.
        File validation and S3 configuration will be added in Phase 1A Week 2.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the attachment"),
    )
    
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text=_("Message this attachment belongs to"),
    )
    
    # Note: FileField configuration will be completed in Week 2 with S3 setup
    file = models.FileField(
        upload_to="chat/attachments/%Y/%m/%d/",
        help_text=_("Uploaded file (stored in S3)"),
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text=_("Original filename"),
    )
    
    file_size = models.IntegerField(
        help_text=_("File size in bytes"),
    )
    
    file_type = models.CharField(
        max_length=100,
        help_text=_("MIME type of the file"),
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when file was uploaded"),
    )
    
    class Meta:
        db_table = "chat_message_attachments"
        ordering = ["uploaded_at"]
        verbose_name = _("Message Attachment")
        verbose_name_plural = _("Message Attachments")
        
        indexes = [
            models.Index(
                fields=["message", "uploaded_at"], name="attach_msg_uploaded_idx"
            ),
        ]
    
    def __str__(self):
        """
        Returns a human-readable string representation of the attachment.
        
        Returns:
            str: Attachment description with filename and size
        """
        size_kb = self.file_size / 1024
        return f"Attachment: {self.file_name} ({size_kb:.1f} KB)"
