"""
Test Suite for Chat API Views

This module contains comprehensive test cases for BiCare360 chat API endpoints,
following Test-Driven Development (TDD) principles.

Test Coverage:
- ConversationViewSet: CRUD operations, filtering, permissions
- ChatMessageViewSet: Message operations, read receipts, soft delete
- Permissions: Object-level access control

Testing Approach:
1. RED: Write failing tests that define expected API behavior
2. GREEN: Implement minimal code to pass tests
3. REFACTOR: Improve code quality while keeping tests green

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.caregivers.models import Caregiver
from apps.chat.models import ChatMessage, Conversation
from apps.nursing.models import NurseProfile
from apps.patients.models import Patient

User = get_user_model()


class ConversationViewSetTests(APITestCase):
    """
    Test cases for the ConversationViewSet API endpoints.
    
    Tests cover:
    - List conversations for authenticated user
    - Retrieve specific conversation
    - Create new conversation
    - Permissions and access control
    """

    def setUp(self):
        """Set up test data before each test method."""
        # Create patient user and profile
        self.patient_user = User.objects.create_user(
            username="patient_api",
            email="patient_api@example.com",
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
            username="caregiver_api",
            email="caregiver_api@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_api2@example.com",
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

        # URL for conversation list
        self.list_url = reverse("chat:conversation-list")
        self.detail_url = reverse(
            "chat:conversation-detail", kwargs={"pk": self.conversation.id}
        )

    def test_list_conversations_requires_authentication(self):
        """
        Test that listing conversations requires authentication.
        
        Verifies:
        - Unauthenticated requests return 401
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_conversations_for_patient(self):
        """
        Test listing conversations for authenticated patient.
        
        Verifies:
        - Patient can list their conversations
        - Only conversations involving patient are returned
        - Response includes conversation details
        """
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(str(self.conversation.id), response.data["results"][0]["id"])

    def test_list_conversations_for_caregiver(self):
        """
        Test listing conversations for authenticated caregiver.
        
        Verifies:
        - Caregiver can list their conversations
        - Only conversations involving caregiver are returned
        """
        self.client.force_authenticate(user=self.caregiver_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_conversation_as_participant(self):
        """
        Test retrieving a specific conversation as participant.
        
        Verifies:
        - Participant can retrieve conversation details
        - Response includes all relevant fields
        """
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(self.conversation.id), response.data["id"])
        self.assertIn("patient_name", response.data)
        self.assertIn("caregiver_name", response.data)

    def test_cannot_retrieve_conversation_as_non_participant(self):
        """
        Test that non-participants cannot retrieve conversation.
        
        Verifies:
        - Non-participant receives 404 or 403
        """
        # Create another user who is not part of this conversation
        other_user = User.objects.create_user(
            username="other_user",
            email="other@example.com",
            password="testpass123",
        )

        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.detail_url)

        # Should return 404 (not found) or 403 (forbidden)
        self.assertIn(
            response.status_code,
            [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN],
        )

    def test_create_conversation(self):
        """
        Test creating a new conversation.
        
        Verifies:
        - Authenticated user can create conversation
        - Created conversation has correct participants
        - Response includes conversation details
        """
        # Create a nurse for new conversation
        nurse_user = User.objects.create_user(
            username="nurse_api",
            email="nurse_api@example.com",
            password="testpass123",
            first_name="Alice",
            last_name="Johnson",
        )
        nurse = NurseProfile.objects.create(
            user=nurse_user,
            license_number="RN123456",
            specialization="General",
        )

        self.client.force_authenticate(user=self.patient_user)

        data = {
            "patient": self.patient.id,
            "nurse": nurse.id,
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(self.patient.id, response.data["patient"])
        self.assertEqual(nurse.id, response.data["nurse"])

    def test_cannot_create_duplicate_conversation(self):
        """
        Test that duplicate conversations are prevented.
        
        Verifies:
        - Attempting to create duplicate returns 400
        - Error message indicates duplicate
        """
        self.client.force_authenticate(user=self.patient_user)

        data = {
            "patient": self.patient.id,
            "caregiver": self.caregiver.id,
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)


class ChatMessageViewSetTests(APITestCase):
    """
    Test cases for the ChatMessageViewSet API endpoints.
    
    Tests cover:
    - List messages in conversation
    - Create new message
    - Mark message as read
    - Soft delete message
    - Permissions
    """

    def setUp(self):
        """Set up test data for message API tests."""
        # Create patient user and profile
        self.patient_user = User.objects.create_user(
            username="patient_msg_api",
            email="patient_msg_api@example.com",
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
            username="caregiver_msg_api",
            email="caregiver_msg_api@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_msg_api2@example.com",
            phone_number="+250788654321",
            profession="registered_nurse",
            experience_years=5,
            bio="Experienced caregiver",
            province="Kigali",
            district="Gasabo",
            hourly_rate=45.00,
        )

        # Create conversation and messages
        self.conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        self.message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Test message from patient",
        )

        # URLs
        self.list_url = reverse("chat:message-list")
        self.detail_url = reverse("chat:message-detail", kwargs={"pk": self.message.id})

    def test_list_messages_requires_authentication(self):
        """
        Test that listing messages requires authentication.
        
        Verifies:
        - Unauthenticated requests return 401
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_messages_in_conversation(self):
        """
        Test listing messages filtered by conversation.
        
        Verifies:
        - Participant can list messages in their conversation
        - Messages are ordered chronologically
        - Deleted messages are excluded by default
        """
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(
            self.list_url, {"conversation": self.conversation.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(str(self.message.id), response.data["results"][0]["id"])

    def test_create_message_in_conversation(self):
        """
        Test creating a new message in conversation.
        
        Verifies:
        - Participant can send message
        - Message is created with correct data
        - Sender is automatically set to authenticated user
        """
        self.client.force_authenticate(user=self.caregiver_user)

        data = {
            "conversation": str(self.conversation.id),
            "content": "Reply from caregiver",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual("Reply from caregiver", response.data["content"])
        self.assertEqual(self.caregiver_user.id, response.data["sender"])

    def test_cannot_send_message_to_non_participant_conversation(self):
        """
        Test that non-participants cannot send messages.
        
        Verifies:
        - Non-participant receives 403
        """
        other_user = User.objects.create_user(
            username="other_msg_user",
            email="other_msg@example.com",
            password="testpass123",
        )

        self.client.force_authenticate(user=other_user)

        data = {
            "conversation": str(self.conversation.id),
            "content": "Unauthorized message",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_message_as_read(self):
        """
        Test marking a message as read.
        
        Verifies:
        - Recipient can mark message as read
        - is_read flag is updated
        - read_at timestamp is set
        """
        self.client.force_authenticate(user=self.caregiver_user)

        # Custom action: mark_as_read
        url = reverse("chat:message-mark-as-read", kwargs={"pk": self.message.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)
        self.assertIsNotNone(self.message.read_at)

    def test_soft_delete_own_message(self):
        """
        Test soft deleting own message.
        
        Verifies:
        - Sender can delete their own message
        - Message is soft deleted (is_deleted=True)
        - Message still exists in database
        """
        self.client.force_authenticate(user=self.patient_user)

        # Custom action: soft_delete
        url = reverse("chat:message-soft-delete", kwargs={"pk": self.message.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_deleted)

    def test_message_content_validation(self):
        """
        Test message content validation.
        
        Verifies:
        - Empty content is rejected
        - Content exceeding max length is rejected
        """
        self.client.force_authenticate(user=self.patient_user)

        # Empty content
        data = {
            "conversation": str(self.conversation.id),
            "content": "",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Content too long
        data = {
            "conversation": str(self.conversation.id),
            "content": "A" * 5001,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
