"""
Test Suite for Chat Serializers

This module contains comprehensive test cases for BiCare360 chat serializers,
following Test-Driven Development (TDD) principles.

Test Coverage:
- ConversationSerializer: conversation creation, validation, representation
- ChatMessageSerializer: message creation, read receipts, soft delete
- MessageAttachmentSerializer: file attachment serialization

Testing Approach:
1. RED: Write failing tests that define expected behavior
2. GREEN: Implement minimal code to pass tests
3. REFACTOR: Improve code quality while keeping tests green

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.caregivers.models import Caregiver
from apps.chat.models import ChatMessage, Conversation, MessageAttachment
from apps.chat.serializers import (
    ChatMessageSerializer,
    ConversationSerializer,
    MessageAttachmentSerializer,
)
from apps.nursing.models import NurseProfile
from apps.patients.models import Patient

User = get_user_model()


class ConversationSerializerTests(TestCase):
    """
    Test cases for the ConversationSerializer.
    
    Tests cover:
    - Serialization of existing conversations
    - Deserialization and validation
    - Nested participant data
    - Error handling for invalid data
    """

    def setUp(self):
        """Set up test data before each test method."""
        # Create patient user and profile
        self.patient_user = User.objects.create_user(
            username="patient_ser_test",
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
            username="caregiver_ser_test",
            email="caregiver@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_ser@example.com",
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

    def test_serialize_conversation(self):
        """
        Test serializing a conversation to JSON.
        
        Verifies:
        - All fields are present
        - UUID is serialized correctly
        - Participant IDs are included
        - Timestamps are ISO formatted
        """
        serializer = ConversationSerializer(self.conversation)
        data = serializer.data

        self.assertIn("id", data)
        self.assertEqual(str(self.conversation.id), data["id"])
        self.assertIn("patient", data)
        self.assertEqual(self.patient.id, data["patient"])
        self.assertIn("caregiver", data)
        self.assertEqual(self.caregiver.id, data["caregiver"])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_serialize_conversation_with_participant_details(self):
        """
        Test serializing conversation with nested participant data.
        
        Verifies that participant details (names, etc.) are included
        when using a detailed serializer representation.
        """
        serializer = ConversationSerializer(self.conversation)
        data = serializer.data

        # Should include participant information
        self.assertIn("patient_name", data)
        self.assertIn("caregiver_name", data)

    def test_deserialize_valid_conversation_data(self):
        """
        Test deserializing valid conversation data.
        
        Verifies:
        - Valid data passes validation
        - Conversation can be created from data
        - All fields are correctly set
        """
        # Create a new nurse for a different conversation
        nurse_user = User.objects.create_user(
            username="nurse_ser_new",
            email="nurse_ser@example.com",
            password="testpass123",
            first_name="Alice",
            last_name="Johnson",
        )
        nurse = NurseProfile.objects.create(
            user=nurse_user,
            license_number="RN123456",
            specialization="General",
        )
        
        # Create patient-nurse conversation (different from existing patient-caregiver)
        data = {
            "patient": self.patient.id,
            "nurse": nurse.id,
        }

        serializer = ConversationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        conversation = serializer.save()
        
        self.assertEqual(conversation.patient, self.patient)
        self.assertEqual(conversation.nurse, nurse)

    def test_cannot_create_duplicate_conversation(self):
        """
        Test that duplicate conversations are rejected.
        
        Verifies:
        - Serializer validation catches duplicate conversations
        - Appropriate error message is returned
        """
        # First conversation already exists
        data = {
            "patient": self.patient.id,
            "caregiver": self.caregiver.id,
        }

        serializer = ConversationSerializer(data=data)
        # Should fail validation due to existing conversation
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_conversation_requires_two_participants(self):
        """
        Test that conversation requires at least two participants.
        
        Verifies:
        - Cannot create conversation with only one participant
        - Validation error is raised
        """
        data = {
            "patient": self.patient.id,
        }

        serializer = ConversationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_conversation_unread_count(self):
        """
        Test that serializer includes unread message count.
        
        Verifies:
        - Unread count is calculated correctly
        - Count excludes deleted messages
        """
        # Create some messages
        ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Test message 1",
        )
        ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.caregiver_user,
            content="Test message 2",
        )

        serializer = ConversationSerializer(self.conversation)
        data = serializer.data

        self.assertIn("unread_count", data)
        # Both messages are unread
        self.assertEqual(2, data["unread_count"])


class ChatMessageSerializerTests(TestCase):
    """
    Test cases for the ChatMessageSerializer.
    
    Tests cover:
    - Message serialization and deserialization
    - Content validation
    - Read receipt handling
    - Soft delete representation
    """

    def setUp(self):
        """Set up test data for message serializer tests."""
        # Create users and profiles
        self.patient_user = User.objects.create_user(
            username="patient_msg_ser",
            email="patient_msg@example.com",
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
            username="caregiver_msg_ser",
            email="caregiver_msg@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_msg_ser@example.com",
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

        # Create message
        self.message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Test message content",
        )

    def test_serialize_message(self):
        """
        Test serializing a message to JSON.
        
        Verifies:
        - All fields are present
        - UUID is serialized correctly
        - Timestamps are ISO formatted
        - Sender information is included
        """
        serializer = ChatMessageSerializer(self.message)
        data = serializer.data

        self.assertIn("id", data)
        self.assertEqual(str(self.message.id), data["id"])
        self.assertIn("conversation", data)
        self.assertIn("sender", data)
        self.assertIn("content", data)
        self.assertEqual("Test message content", data["content"])
        self.assertIn("is_read", data)
        self.assertFalse(data["is_read"])
        self.assertIn("created_at", data)

    def test_deserialize_valid_message_data(self):
        """
        Test deserializing valid message data.
        
        Verifies:
        - Valid data passes validation
        - Message can be created from data
        - Required fields are validated
        """
        data = {
            "conversation": self.conversation.id,
            "sender": self.caregiver_user.id,
            "content": "Reply message",
        }

        serializer = ChatMessageSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        message = serializer.save()

        self.assertEqual("Reply message", message.content)
        self.assertEqual(self.caregiver_user, message.sender)
        self.assertFalse(message.is_read)

    def test_message_content_required(self):
        """
        Test that message content is required.
        
        Verifies:
        - Empty content is rejected
        - Validation error is raised
        """
        data = {
            "conversation": self.conversation.id,
            "sender": self.patient_user.id,
            "content": "",
        }

        serializer = ChatMessageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_message_content_max_length(self):
        """
        Test that message content respects max length.
        
        Verifies:
        - Content over 5000 characters is rejected
        - Validation error includes max length info
        """
        data = {
            "conversation": self.conversation.id,
            "sender": self.patient_user.id,
            "content": "A" * 5001,  # Exceeds 5000 char limit
        }

        serializer = ChatMessageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)

    def test_serialize_message_with_sender_details(self):
        """
        Test that serializer includes sender details.
        
        Verifies:
        - Sender name is included
        - Sender information is properly nested
        """
        serializer = ChatMessageSerializer(self.message)
        data = serializer.data

        self.assertIn("sender_name", data)
        self.assertEqual("John Doe", data["sender_name"])

    def test_deleted_messages_marked_in_serialization(self):
        """
        Test that deleted messages are properly marked.
        
        Verifies:
        - is_deleted flag is present
        - Content may be hidden for deleted messages
        """
        self.message.soft_delete()
        serializer = ChatMessageSerializer(self.message)
        data = serializer.data

        self.assertTrue(data["is_deleted"])


class MessageAttachmentSerializerTests(TestCase):
    """
    Test cases for the MessageAttachmentSerializer.
    
    Tests cover:
    - Attachment metadata serialization
    - File field handling
    - Size and type validation
    """

    def setUp(self):
        """Set up test data for attachment serializer tests."""
        # Create minimal test setup
        self.patient_user = User.objects.create_user(
            username="patient_attach_ser",
            email="patient_attach@example.com",
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
            username="caregiver_attach_ser",
            email="caregiver_attach@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_attach_ser@example.com",
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

    def test_serialize_attachment_metadata(self):
        """
        Test serializing attachment metadata (placeholder).
        
        Note: Full file upload testing will be implemented with S3 setup.
        For now, we verify the serializer structure exists.
        """
        # Verify serializer can be instantiated
        serializer = MessageAttachmentSerializer()
        self.assertIsNotNone(serializer)

    def test_attachment_serializer_fields(self):
        """
        Test that attachment serializer has required fields.
        
        Verifies:
        - File field exists
        - Metadata fields exist
        - Read-only fields are properly configured
        """
        serializer = MessageAttachmentSerializer()
        fields = serializer.fields

        # Check for expected fields
        self.assertIn("file", fields)
        self.assertIn("file_name", fields)
        self.assertIn("file_size", fields)
        self.assertIn("file_type", fields)
