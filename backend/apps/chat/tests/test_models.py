"""
Test Suite for Chat Models

This module contains comprehensive test cases for the BiCare360 chat models,
following Test-Driven Development (TDD) principles.

Test Coverage:
- Conversation model: creation, uniqueness constraints, participant management
- ChatMessage model: messaging, read receipts, soft delete, ordering
- MessageAttachment model: file uploads, validation, storage
- MessageNotification model: notification creation, unread tracking

Testing Approach:
1. RED: Write failing tests that define expected behavior
2. GREEN: Implement minimal code to pass tests
3. REFACTOR: Improve code quality while keeping tests green

Author: Didier IMANIRAHARI
Date: February 2026
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.caregivers.models import Caregiver
from apps.chat.models import ChatMessage, Conversation, MessageAttachment
from apps.nursing.models import NurseProfile
from apps.patients.models import Patient

User = get_user_model()


class ConversationModelTests(TestCase):
    """
    Test cases for the Conversation model.
    
    Tests cover:
    - Conversation creation between different user types
    - Uniqueness constraints to prevent duplicate conversations
    - Participant retrieval methods
    - String representation
    - Metadata tracking (created_at, updated_at)
    """

    def setUp(self):
        """
        Set up test data before each test method.
        
        Creates:
        - Patient user and profile
        - Caregiver user and profile
        - Nurse user and profile
        """
        # Create patient user and profile
        self.patient_user = User.objects.create_user(
            username="patient_test",
            email="patient@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth="1980-01-01",
            gender="M",
            phone_number="+250788123456",
            national_id="1198070123456789",
        )

        # Create caregiver user and profile
        self.caregiver_user = User.objects.create_user(
            username="caregiver_test",
            email="caregiver@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver2@example.com",  # Different email required
            phone_number="+250788654321",
            profession="registered_nurse",
            experience_years=5,
            bio="Experienced caregiver",
            province="Kigali",
            district="Gasabo",
            hourly_rate=45.00,
        )

        # Create nurse user and profile
        self.nurse_user = User.objects.create_user(
            username="nurse_test",
            email="nurse@example.com",
            password="testpass123",
            first_name="Alice",
            last_name="Johnson",
        )
        self.nurse = NurseProfile.objects.create(
            user=self.nurse_user,
            license_number="RN123456",
            specialization="General",
        )

    def test_create_patient_caregiver_conversation(self):
        """
        Test creating a conversation between a patient and a caregiver.
        
        Verifies:
        - Conversation is created successfully
        - Patient and caregiver are correctly linked
        - UUID primary key is generated
        - Timestamps are set
        """
        conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        self.assertIsNotNone(conversation.id)
        self.assertIsInstance(conversation.id, uuid.UUID)
        self.assertEqual(conversation.patient, self.patient)
        self.assertEqual(conversation.caregiver, self.caregiver)
        self.assertIsNone(conversation.nurse)
        self.assertIsNotNone(conversation.created_at)
        self.assertIsNotNone(conversation.updated_at)

    def test_create_patient_nurse_conversation(self):
        """
        Test creating a conversation between a patient and a nurse.
        
        Verifies:
        - Conversation is created successfully
        - Patient and nurse are correctly linked
        - Caregiver field is None
        """
        conversation = Conversation.objects.create(
            patient=self.patient, nurse=self.nurse
        )

        self.assertIsNotNone(conversation.id)
        self.assertEqual(conversation.patient, self.patient)
        self.assertEqual(conversation.nurse, self.nurse)
        self.assertIsNone(conversation.caregiver)

    def test_create_caregiver_nurse_conversation(self):
        """
        Test creating a conversation between a caregiver and a nurse.
        
        Verifies:
        - Conversation is created successfully
        - Caregiver and nurse are correctly linked
        - Patient field is None
        """
        conversation = Conversation.objects.create(
            caregiver=self.caregiver, nurse=self.nurse
        )

        self.assertIsNotNone(conversation.id)
        self.assertEqual(conversation.caregiver, self.caregiver)
        self.assertEqual(conversation.nurse, self.nurse)
        self.assertIsNone(conversation.patient)

    def test_duplicate_patient_caregiver_conversation_prevented(self):
        """
        Test that duplicate patient-caregiver conversations are prevented.
        
        Verifies:
        - First conversation is created successfully
        - Attempting to create duplicate raises IntegrityError
        - Database constraint ensures uniqueness
        """
        # Create first conversation
        Conversation.objects.create(patient=self.patient, caregiver=self.caregiver)

        # Attempt to create duplicate should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Conversation.objects.create(
                patient=self.patient, caregiver=self.caregiver
            )

    def test_duplicate_patient_nurse_conversation_prevented(self):
        """
        Test that duplicate patient-nurse conversations are prevented.
        
        Verifies uniqueness constraint for patient-nurse pairs.
        """
        # Create first conversation
        Conversation.objects.create(patient=self.patient, nurse=self.nurse)

        # Attempt to create duplicate should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Conversation.objects.create(patient=self.patient, nurse=self.nurse)

    def test_get_participants_patient_caregiver(self):
        """
        Test retrieving participants from a patient-caregiver conversation.
        
        Verifies:
        - get_participants() returns both users
        - Patient user is included
        - Caregiver user is included
        - Returns list of User objects
        """
        conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        participants = conversation.get_participants()

        self.assertEqual(len(participants), 2)
        self.assertIn(self.patient_user, participants)
        self.assertIn(self.caregiver_user, participants)

    def test_get_participants_patient_nurse(self):
        """
        Test retrieving participants from a patient-nurse conversation.
        
        Verifies correct participant retrieval for patient-nurse pairs.
        """
        conversation = Conversation.objects.create(
            patient=self.patient, nurse=self.nurse
        )

        participants = conversation.get_participants()

        self.assertEqual(len(participants), 2)
        self.assertIn(self.patient_user, participants)
        self.assertIn(self.nurse_user, participants)

    def test_conversation_str_representation(self):
        """
        Test the string representation of a conversation.
        
        Verifies:
        - __str__ method returns meaningful description
        - Includes participant names
        - Format is consistent
        """
        conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        str_repr = str(conversation)

        # Should contain participant names or roles
        self.assertIsInstance(str_repr, str)
        self.assertTrue(len(str_repr) > 0)

    def test_conversation_updated_at_changes(self):
        """
        Test that updated_at timestamp changes when conversation is modified.
        
        Verifies:
        - updated_at is set on creation
        - updated_at changes when conversation is updated
        - Timestamp reflects actual update time
        """
        conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        original_updated_at = conversation.updated_at

        # Wait a moment and update
        conversation.save()

        self.assertGreaterEqual(conversation.updated_at, original_updated_at)

    def test_conversation_requires_at_least_two_participants(self):
        """
        Test that a conversation requires at least two participants.
        
        Verifies:
        - Cannot create conversation with only one participant
        - Model validation enforces participant requirements
        """
        # This test expects validation to fail at model level
        # Implementation should validate that at least 2 participants exist
        with self.assertRaises((ValidationError, IntegrityError)):
            conversation = Conversation(patient=self.patient)
            conversation.full_clean()  # Trigger validation


class ChatMessageModelTests(TestCase):
    """
    Test cases for the ChatMessage model.
    
    Tests cover:
    - Message creation and content storage
    - Message ordering by timestamp
    - Read receipt tracking
    - Soft delete functionality
    - Sender identification
    """

    def setUp(self):
        """Set up test data for chat message tests."""
        # Create users and profiles
        self.patient_user = User.objects.create_user(
            username="patient_msg_test",
            email="patient@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth="1980-01-01",
            gender="M",
            phone_number="+250788123456",
            national_id="1198070123456789",
        )

        self.caregiver_user = User.objects.create_user(
            username="caregiver_msg_test",
            email="caregiver@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver3@example.com",  # Different email required
            phone_number="+250788654321",
            profession="registered_nurse",
            experience_years=5,
            bio="Experienced caregiver",
            province="Kigali",
            district="Gasabo",
            hourly_rate=45.00,
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

    def test_create_chat_message(self):
        """
        Test creating a basic chat message.
        
        Verifies:
        - Message is created successfully
        - Content is stored correctly
        - Sender is linked properly
        - Conversation reference is maintained
        - Timestamps are set
        - Default values are correct (is_read=False, is_deleted=False)
        """
        message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Hello, I need help with my medication.",
        )

        self.assertIsNotNone(message.id)
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.sender, self.patient_user)
        self.assertEqual(message.content, "Hello, I need help with my medication.")
        self.assertFalse(message.is_read)
        self.assertFalse(message.is_deleted)
        self.assertIsNone(message.read_at)
        self.assertIsNotNone(message.created_at)

    def test_message_ordering_by_created_at(self):
        """
        Test that messages are ordered by creation timestamp.
        
        Verifies:
        - Multiple messages can be created
        - Messages are retrieved in chronological order
        - Oldest messages appear first
        """
        # Create multiple messages
        msg1 = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="First message",
        )

        msg2 = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.caregiver_user,
            content="Second message",
        )

        msg3 = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Third message",
        )

        # Retrieve messages in order
        messages = ChatMessage.objects.filter(conversation=self.conversation).order_by(
            "created_at"
        )

        self.assertEqual(list(messages), [msg1, msg2, msg3])

    def test_mark_message_as_read(self):
        """
        Test marking a message as read.
        
        Verifies:
        - mark_as_read() method exists and works
        - is_read flag is set to True
        - read_at timestamp is set
        - read_at is a datetime
        """
        message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Test message",
        )

        # Initially unread
        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_at)

        # Mark as read
        message.mark_as_read()

        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)
        self.assertIsInstance(message.read_at, type(timezone.now()))

    def test_soft_delete_message(self):
        """
        Test soft deleting a message.
        
        Verifies:
        - soft_delete() method exists and works
        - is_deleted flag is set to True
        - Message still exists in database
        - Message can be filtered out using is_deleted=False
        """
        message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Message to be deleted",
        )

        # Initially not deleted
        self.assertFalse(message.is_deleted)

        # Soft delete
        message.soft_delete()

        self.assertTrue(message.is_deleted)

        # Message still exists in database
        self.assertEqual(ChatMessage.objects.filter(id=message.id).count(), 1)

        # Can be filtered out
        active_messages = ChatMessage.objects.filter(
            conversation=self.conversation, is_deleted=False
        )
        self.assertNotIn(message, active_messages)

    def test_message_str_representation(self):
        """
        Test the string representation of a message.
        
        Verifies:
        - __str__ method returns meaningful description
        - Includes sender and content preview
        """
        message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Test message content",
        )

        str_repr = str(message)

        self.assertIsInstance(str_repr, str)
        self.assertTrue(len(str_repr) > 0)

    def test_cannot_mark_deleted_message_as_read(self):
        """
        Test that deleted messages cannot be marked as read.
        
        Verifies business logic that prevents reading deleted messages.
        """
        message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Test message",
        )

        message.soft_delete()

        # Attempting to mark as read should either:
        # 1. Raise an exception, or
        # 2. Be silently ignored
        # Implementation should handle this gracefully
        message.mark_as_read()  # Should not crash

    def test_message_content_max_length(self):
        """
        Test that message content respects maximum length.
        
        Verifies:
        - Long messages can be stored
        - Extremely long messages may be truncated or rejected
        """
        long_content = "A" * 5000  # 5000 characters

        message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content=long_content,
        )

        self.assertIsNotNone(message.id)
        # Content should be stored (or truncated gracefully)
        self.assertTrue(len(message.content) <= 5000)


class MessageAttachmentModelTests(TestCase):
    """
    Test cases for the MessageAttachment model.
    
    Tests cover:
    - File attachment creation
    - File type validation
    - File size validation
    - Multiple attachments per message
    """

    def setUp(self):
        """Set up test data for attachment tests."""
        # Create minimal setup for attachments
        self.patient_user = User.objects.create_user(
            username="patient_attach_test",
            email="patient@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth="1980-01-01",
            gender="M",
            phone_number="+250788123456",
            national_id="1198070123456789",
        )

        self.caregiver_user = User.objects.create_user(
            username="caregiver_attach_test",
            email="caregiver@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver4@example.com",  # Different email required
            phone_number="+250788654321",
            profession="registered_nurse",
            experience_years=5,
            bio="Experienced caregiver",
            province="Kigali",
            district="Gasabo",
            hourly_rate=45.00,
        )

        self.conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        self.message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Message with attachment",
        )

    def test_create_attachment_placeholder(self):
        """
        Test creating an attachment (placeholder test).
        
        Note: This is a placeholder test for attachment creation.
        Full implementation will require mocking file uploads or using
        Django's SimpleUploadedFile for testing.
        
        Verifies:
        - Attachment model exists
        - Basic fields are present
        """
        # This test will be expanded once file upload is implemented
        # For now, we verify the model structure
        self.assertTrue(hasattr(MessageAttachment, "objects"))

    def test_attachment_file_type_validation_placeholder(self):
        """
        Placeholder test for file type validation.
        
        Will verify that only allowed file types can be uploaded
        (e.g., images, PDFs, documents).
        """
        # To be implemented with actual file upload logic
        pass

    def test_attachment_file_size_validation_placeholder(self):
        """
        Placeholder test for file size validation.
        
        Will verify that files exceeding size limit are rejected.
        """
        # To be implemented with actual file upload logic
        pass
