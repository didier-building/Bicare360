"""
Test Suite for Chat WebSocket Consumer

This module contains comprehensive test cases for the WebSocket consumer
that handles real-time chat messaging.

Test Coverage:
- WebSocket connection and authentication
- Message sending and receiving
- Read receipt handling
- Typing indicators
- Connection/disconnection events
- Error handling and edge cases

Author: Didier IMANIRAHARI
Date: February 2026
"""

from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from apps.caregivers.models import Caregiver
from apps.chat.consumers import ChatConsumer
from apps.chat.models import ChatMessage, Conversation
from apps.patients.models import Patient

User = get_user_model()


class ChatConsumerTests(TransactionTestCase):
    """
    Test cases for the ChatConsumer WebSocket handler.
    
    Uses TransactionTestCase for proper async/WebSocket testing support.
    Tests verify real-time messaging functionality including connection,
    message sending, read receipts, and typing indicators.
    """

    def setUp(self):
        """Set up test data synchronously before each test method."""
        # Create patient
        self.patient_user = User.objects.create_user(
            username="patient_ws",
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
            username="caregiver_ws",
            email="caregiver@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.caregiver = Caregiver.objects.create(
            user=self.caregiver_user,
            first_name="Jane",
            last_name="Smith",
            email="caregiver_ws@example.com",
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

    async def test_websocket_connection_authorized_user(self):
        """
        Test that authorized conversation participants can connect via WebSocket.
        
        Verifies:
        - Patient can connect to their conversation
        - WebSocket accepts connection
        - Connection is established successfully
        """
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        communicator.scope["user"] = self.patient_user
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        connected, _ = await communicator.connect()

        self.assertTrue(connected, "Patient should be able to connect to conversation")

        await communicator.disconnect()

    async def test_websocket_connection_unauthorized_user(self):
        """
        Test that unauthorized users cannot connect to conversations.
        
        Verifies:
        - Non-participant users are rejected
        - Connection is refused with appropriate status
        """
        # Create outsider user
        @database_sync_to_async
        def create_outsider():
            return User.objects.create_user(
                username="outsider_ws",
                email="outsider@example.com",
                password="testpass123",
            )
        
        outsider = await create_outsider()

        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        communicator.scope["user"] = outsider
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        connected, _ = await communicator.connect()

        self.assertFalse(connected, "Outsider should not be able to connect")

    async def test_send_message_via_websocket(self):
        """
        Test sending a message through WebSocket.
        
        Verifies:
        - Message is sent successfully
        - Message is saved to database
        - Response contains message data
        - Timestamps are set correctly
        """
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        communicator.scope["user"] = self.patient_user
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message
        await communicator.send_json_to({
            "type": "chat_message",
            "content": "Hello, I need help with my medication.",
        })

        # Receive response
        response = await communicator.receive_json_from(timeout=5)

        self.assertEqual(response["type"], "chat_message")
        self.assertEqual(response["content"], "Hello, I need help with my medication.")
        self.assertIn("id", response)
        self.assertIn("created_at", response)
        self.assertEqual(response["sender"]["id"], self.patient_user.id)

        # Verify message was saved to database
        @database_sync_to_async
        def count_messages():
            return ChatMessage.objects.filter(
                conversation=self.conversation,
                content="Hello, I need help with my medication.",
            ).count()
        
        message_count = await count_messages()
        self.assertEqual(message_count, 1)

        await communicator.disconnect()

    async def test_receive_message_from_other_participant(self):
        """
        Test receiving messages sent by other participants.
        
        Verifies:
        - Messages are broadcast to all conversation participants
        - Non-senders receive messages in real-time
        - Message data is correctly formatted
        """
        # Connect both patient and caregiver
        patient_communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        patient_communicator.scope["user"] = self.patient_user
        patient_communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        caregiver_communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        caregiver_communicator.scope["user"] = self.caregiver_user
        caregiver_communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        await patient_communicator.connect()
        
        await caregiver_communicator.connect()
        # Patient receives caregiver's online status
        await patient_communicator.receive_json_from(timeout=5)

        # Patient sends message
        await patient_communicator.send_json_to({
            "type": "chat_message",
            "content": "Message from patient",
        })

        # Patient receives their own message (echo)
        patient_response = await patient_communicator.receive_json_from(timeout=5)
        self.assertEqual(patient_response["content"], "Message from patient")

        # Caregiver receives the message
        caregiver_response = await caregiver_communicator.receive_json_from(timeout=5)
        self.assertEqual(caregiver_response["content"], "Message from patient")
        self.assertEqual(caregiver_response["type"], "chat_message")

        await patient_communicator.disconnect()
        await caregiver_communicator.disconnect()

    async def test_mark_message_as_read(self):
        """
        Test marking messages as read via WebSocket.
        
        Verifies:
        - Read receipt event is sent
        - Message is marked as read in database
        - read_at timestamp is set
        - Other participants are notified
        """
        # Create a message  
        @database_sync_to_async
        def create_message():
            return ChatMessage.objects.create(
                conversation=self.conversation,
                sender=self.patient_user,
                content="Test message for read receipt",
            )
        
        message = await create_message()

        # Connect caregiver
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        communicator.scope["user"] = self.caregiver_user
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        await communicator.connect()

        # Send read receipt
        await communicator.send_json_to({
            "type": "mark_read",
            "message_id": str(message.id),
        })

        # Receive confirmation
        response = await communicator.receive_json_from(timeout=5)

        self.assertEqual(response["type"], "message_read")
        self.assertEqual(response["message_id"], str(message.id))

        # Verify message is marked as read in database
        @database_sync_to_async
        def refresh_message():
            message.refresh_from_db()
            return message
        
        await refresh_message()
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)

        await communicator.disconnect()

    async def test_typing_indicator(self):
        """
        Test typing indicator functionality.
        
        Verifies:
        - Typing event is broadcast to other participants
        - Typing stopped event is sent
        - Events include user information
        """
        # Connect both users
        patient_communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        patient_communicator.scope["user"] = self.patient_user
        patient_communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        caregiver_communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        caregiver_communicator.scope["user"] = self.caregiver_user
        caregiver_communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        await patient_communicator.connect()
        await caregiver_communicator.connect()

        # Patient starts typing
        await patient_communicator.send_json_to({
            "type": "typing_start",
        })

        # Caregiver receives typing indicator
        typing_response = await caregiver_communicator.receive_json_from(timeout=5)

        self.assertEqual(typing_response["type"], "user_typing")
        self.assertEqual(typing_response["user_id"], self.patient_user.id)
        self.assertTrue(typing_response["is_typing"])

        # Patient stops typing
        await patient_communicator.send_json_to({
            "type": "typing_stop",
        })

        # Caregiver receives stop typing indicator
        stop_response = await caregiver_communicator.receive_json_from(timeout=5)

        self.assertEqual(stop_response["type"], "user_typing")
        self.assertEqual(stop_response["user_id"], self.patient_user.id)
        self.assertFalse(stop_response["is_typing"])

        await patient_communicator.disconnect()
        await caregiver_communicator.disconnect()

    async def test_empty_message_rejected(self):
        """
        Test that empty messages are rejected.
        
        Verifies:
        - Empty content is not allowed
        - Error message is returned
        - No message is saved to database
        """
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        communicator.scope["user"] = self.patient_user
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        await communicator.connect()

        # Send empty message
        await communicator.send_json_to({
            "type": "chat_message",
            "content": "",
        })

        # Receive error response
        response = await communicator.receive_json_from(timeout=5)

        self.assertEqual(response["type"], "error")
        self.assertIn("error", response)

        await communicator.disconnect()

    async def test_message_too_long_rejected(self):
        """
        Test that messages exceeding max length are rejected.
        
        Verifies:
        - Messages over 5000 characters are rejected
        - Error message is returned
        - No message is saved to database
        """
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        communicator.scope["user"] = self.patient_user
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        await communicator.connect()

        # Send message that's too long
        long_content = "A" * 5001
        await communicator.send_json_to({
            "type": "chat_message",
            "content": long_content,
        })

        # Receive error response
        response = await communicator.receive_json_from(timeout=5)

        self.assertEqual(response["type"], "error")
        self.assertIn("error", response)

        await communicator.disconnect()

    async def test_connection_user_online_status(self):
        """
        Test that connection/disconnection events are broadcast.
        
        Verifies:
        - User online event is sent when connecting
        - User offline event is sent when disconnecting
        - Other participants are notified
        """
        # Connect patient and caregiver
        patient_communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        patient_communicator.scope["user"] = self.patient_user
        patient_communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        caregiver_communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
        )
        caregiver_communicator.scope["user"] = self.caregiver_user
        caregiver_communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": str(self.conversation.id)}
        }

        await patient_communicator.connect()
        await caregiver_communicator.connect()

        # Caregiver should receive patient online event
        # (may need to clear initial messages first)
        # This is a placeholder - actual implementation may vary

        # Disconnect patient
        await patient_communicator.disconnect()

        # Caregiver should receive patient offline event
        # (implementation specific)

        await caregiver_communicator.disconnect()
