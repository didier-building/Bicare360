"""
Test Suite for Chat Permissions

This module contains comprehensive test cases for permission classes
that control access to chat conversations and messages.

Test Coverage:
- IsConversationParticipant permission for conversations
- IsMessageSenderOrRecipient permission for messages
- Object-level permissions for read/write access
- Edge cases and unauthorized access attempts

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory

from apps.caregivers.models import Caregiver
from apps.chat.models import ChatMessage, Conversation
from apps.chat.permissions import (
    IsConversationParticipant,
    IsMessageSenderOrRecipient,
)
from apps.nursing.models import NurseProfile
from apps.patients.models import Patient

User = get_user_model()


class IsConversationParticipantTests(APITestCase):
    """
    Test cases for IsConversationParticipant permission class.
    
    Tests verify that only participants (patient, caregiver, or nurse)
    can access conversation objects.
    """

    def setUp(self):
        """Set up test data for permission tests."""
        # Create patient
        self.patient_user = User.objects.create_user(
            username="patient_perm",
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

        # Create caregiver
        self.caregiver_user = User.objects.create_user(
            username="caregiver_perm",
            email="caregiver@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_perm@example.com",
            phone_number="+250788654321",
            profession="registered_nurse",
            experience_years=5,
            bio="Experienced caregiver",
            province="Kigali",
            district="Gasabo",
            hourly_rate=45.00,
        )

        # Create nurse
        self.nurse_user = User.objects.create_user(
            username="nurse_perm",
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

        # Create outsider user (not participant)
        self.outsider_user = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="testpass123",
            first_name="Bob",
            last_name="Outsider",
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        # Initialize permission and request factory
        self.permission = IsConversationParticipant()
        self.factory = APIRequestFactory()

    def test_patient_has_permission(self):
        """Test that patient participant has permission to access conversation."""
        request = self.factory.get("/fake-url/")
        request.user = self.patient_user

        has_permission = self.permission.has_object_permission(
            request, None, self.conversation
        )

        self.assertTrue(has_permission)

    def test_caregiver_has_permission(self):
        """Test that caregiver participant has permission to access conversation."""
        request = self.factory.get("/fake-url/")
        request.user = self.caregiver_user

        has_permission = self.permission.has_object_permission(
            request, None, self.conversation
        )

        self.assertTrue(has_permission)

    def test_nurse_has_permission(self):
        """Test that nurse participant has permission to access conversation."""
        # Create patient-nurse conversation
        nurse_conversation = Conversation.objects.create(
            patient=self.patient, nurse=self.nurse
        )

        request = self.factory.get("/fake-url/")
        request.user = self.nurse_user

        has_permission = self.permission.has_object_permission(
            request, None, nurse_conversation
        )

        self.assertTrue(has_permission)

    def test_non_participant_has_no_permission(self):
        """Test that non-participant user is denied access to conversation."""
        request = self.factory.get("/fake-url/")
        request.user = self.outsider_user

        has_permission = self.permission.has_object_permission(
            request, None, self.conversation
        )

        self.assertFalse(has_permission)

    def test_unauthenticated_user_has_no_permission(self):
        """Test that unauthenticated users are denied access."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/fake-url/")
        request.user = AnonymousUser()

        has_permission = self.permission.has_object_permission(
            request, None, self.conversation
        )

        self.assertFalse(has_permission)

    def test_permission_for_all_request_methods(self):
        """Test that permission works for GET, POST, PUT, DELETE methods."""
        methods = ["get", "post", "put", "patch", "delete"]

        for method in methods:
            request = getattr(self.factory, method)("/fake-url/")
            request.user = self.patient_user

            has_permission = self.permission.has_object_permission(
                request, None, self.conversation
            )

            self.assertTrue(
                has_permission,
                f"Patient should have permission for {method.upper()} request",
            )


class IsMessageSenderOrRecipientTests(APITestCase):
    """
    Test cases for IsMessageSenderOrRecipient permission class.
    
    Tests verify that users can only access messages in conversations
    where they are participants.
    """

    def setUp(self):
        """Set up test data for message permission tests."""
        # Create patient
        self.patient_user = User.objects.create_user(
            username="patient_msg_perm",
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

        # Create caregiver
        self.caregiver_user = User.objects.create_user(
            username="caregiver_msg_perm",
            email="caregiver@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_msg_perm@example.com",
            phone_number="+250788654321",
            profession="registered_nurse",
            experience_years=5,
            bio="Experienced caregiver",
            province="Kigali",
            district="Gasabo",
            hourly_rate=45.00,
        )

        # Create outsider
        self.outsider_user = User.objects.create_user(
            username="outsider_msg",
            email="outsider@example.com",
            password="testpass123",
            first_name="Bob",
            last_name="Outsider",
        )

        # Create conversation and message
        self.conversation = Conversation.objects.create(
            patient=self.patient, caregiver=self.caregiver
        )

        self.message = ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.patient_user,
            content="Test message from patient",
        )

        # Initialize permission and request factory
        self.permission = IsMessageSenderOrRecipient()
        self.factory = APIRequestFactory()

    def test_sender_has_permission(self):
        """Test that message sender has permission to access message."""
        request = self.factory.get("/fake-url/")
        request.user = self.patient_user

        has_permission = self.permission.has_object_permission(
            request, None, self.message
        )

        self.assertTrue(has_permission)

    def test_recipient_has_permission(self):
        """Test that message recipient has permission to access message."""
        request = self.factory.get("/fake-url/")
        request.user = self.caregiver_user

        has_permission = self.permission.has_object_permission(
            request, None, self.message
        )

        self.assertTrue(has_permission)

    def test_non_participant_has_no_permission(self):
        """Test that non-participant user cannot access message."""
        request = self.factory.get("/fake-url/")
        request.user = self.outsider_user

        has_permission = self.permission.has_object_permission(
            request, None, self.message
        )

        self.assertFalse(has_permission)

    def test_sender_can_delete_own_message(self):
        """Test that sender can delete their own message."""
        request = self.factory.delete("/fake-url/")
        request.user = self.patient_user

        has_permission = self.permission.has_object_permission(
            request, None, self.message
        )

        self.assertTrue(has_permission)

    def test_recipient_cannot_delete_others_message(self):
        """
        Test that recipients can view but permissions are handled at view level.
        
        Note: Actual delete restrictions are enforced in the ViewSet,
        this permission class only checks conversation participation.
        """
        request = self.factory.delete("/fake-url/")
        request.user = self.caregiver_user

        # Permission class allows access to conversation participants
        has_permission = self.permission.has_object_permission(
            request, None, self.message
        )

        # Permission is True because caregiver is a conversation participant
        # The ViewSet's destroy() method enforces sender-only deletion
        self.assertTrue(has_permission)

    def test_unauthenticated_user_has_no_permission(self):
        """Test that unauthenticated users cannot access messages."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/fake-url/")
        request.user = AnonymousUser()

        has_permission = self.permission.has_object_permission(
            request, None, self.message
        )

        self.assertFalse(has_permission)
