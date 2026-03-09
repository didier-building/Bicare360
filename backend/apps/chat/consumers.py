"""
WebSocket Consumer for BiCare360 Real-Time Chat

This module implements the WebSocket consumer that handles real-time
messaging between patients, caregivers, and nurses.

Features:
    - Real-time message sending and receiving
    - Read receipt tracking
    - Typing indicators
    - User online/offline status
    - Message validation
    - Authentication and authorization

WebSocket Events:
    Incoming:
        - chat_message: Send a new message
        - mark_read: Mark a message as read
        - typing_start: User started typing
        - typing_stop: User stopped typing
    
    Outgoing:
        - chat_message: New message received
        - message_read: Message marked as read
        - user_typing: Typing indicator
        - user_status: Online/offline status
        - error: Error message

Security:
    - JWT authentication via WebSocket headers
    - Participant-only access verification
    - Message sanitization and validation

Author: Didier IMANIRAHARI
Date: February 2026
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from apps.chat.models import ChatMessage, Conversation


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat messaging.
    
    This consumer manages WebSocket connections for chat conversations,
    handling message sending, read receipts, typing indicators, and
    user presence.
    
    Attributes:
        conversation_id (str): UUID of the conversation
        conversation_group_name (str): Channel group name for broadcasting
        conversation (Conversation): Conversation model instance
        user: Authenticated user from WebSocket scope
    
    Connection Flow:
        1. User connects with conversation_id in URL
        2. Verify user is a conversation participant
        3. Join conversation channel group
        4. Broadcast user online status
        5. Handle incoming events
        6. On disconnect, broadcast user offline status
    
    Examples:
        WebSocket URL: ws://domain/ws/chat/<conversation_id>/
        
        Send message:
        {
            "type": "chat_message",
            "content": "Hello, I need help"
        }
        
        Mark message as read:
        {
            "type": "mark_read",
            "message_id": "uuid-here"
        }
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        
        Verifies:
        - User is authenticated
        - User is a conversation participant
        - Conversation exists
        
        If authorized, accepts connection and joins conversation group.
        Otherwise, closes connection with 403 status.
        """
        # Extract conversation_id from URL route
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.conversation_group_name = f"chat_{self.conversation_id}"
        
        # Get authenticated user from scope
        self.user = self.scope["user"]
        
        # Verify user is authenticated
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Unauthorized
            return
        
        # Load conversation and verify user is a participant
        try:
            self.conversation = await self.get_conversation()
            
            if not await self.is_participant():
                await self.close(code=4003)  # Forbidden
                return
            
        except Conversation.DoesNotExist:
            await self.close(code=4004)  # Not found
            return
        
        # Accept WebSocket connection
        await self.accept()
        
        # Join conversation group for real-time broadcasting
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        # Broadcast user online status to conversation participants
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                "type": "user_status",
                "user_id": self.user.id,
                "username": self.user.get_full_name(),
                "status": "online",
            }
        )

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        
        Broadcasts user offline status and removes from conversation group.
        
        Args:
            close_code (int): WebSocket close code
        """
        # Broadcast user offline status
        if hasattr(self, "conversation_group_name"):
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "username": self.user.get_full_name(),
                    "status": "offline",
                }
            )
            
            # Leave conversation group
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        
        Routes messages to appropriate handlers based on message type.
        
        Args:
            text_data (str): JSON string containing message data
        
        Message Types:
            - chat_message: New message to send
            - mark_read: Mark message as read
            - typing_start: User started typing
            - typing_stop: User stopped typing
        """
        try:
            data = json.loads(text_data)
            message_type = data.get("type")
            
            if message_type == "chat_message":
                await self.handle_chat_message(data)
            elif message_type == "mark_read":
                await self.handle_mark_read(data)
            elif message_type == "typing_start":
                await self.handle_typing_start()
            elif message_type == "typing_stop":
                await self.handle_typing_stop()
            else:
                await self.send_error("Unknown message type")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            await self.send_error(f"Error processing message: {str(e)}")

    async def handle_chat_message(self, data):
        """
        Handle sending a new chat message.
        
        Validates message content, saves to database, and broadcasts
        to all conversation participants.
        
        Args:
            data (dict): Message data containing 'content' field
        
        Validation:
            - Content must not be empty
            - Content must not exceed 5000 characters
        """
        content = data.get("content", "").strip()
        
        # Validate message content
        if not content:
            await self.send_error("Message content cannot be empty")
            return
        
        if len(content) > 5000:
            await self.send_error("Message content exceeds maximum length (5000 characters)")
            return
        
        # Save message to database
        message = await self.save_message(content)
        
        # Broadcast message to all conversation participants
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                "type": "chat_message",
                "message_id": str(message.id),
                "content": message.content,
                "sender": {
                    "id": self.user.id,
                    "name": self.user.get_full_name(),
                    "email": self.user.email,
                },
                "created_at": message.created_at.isoformat(),
                "is_read": message.is_read,
            }
        )

    async def handle_mark_read(self, data):
        """
        Handle marking a message as read.
        
        Updates message read status and broadcasts read receipt.
        
        Args:
            data (dict): Data containing 'message_id' field
        """
        message_id = data.get("message_id")
        
        if not message_id:
            await self.send_error("Message ID is required")
            return
        
        # Mark message as read in database
        success = await self.mark_message_read(message_id)
        
        if success:
            # Broadcast read receipt to conversation participants
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    "type": "message_read",
                    "message_id": message_id,
                    "read_by_user_id": self.user.id,
                    "read_at": timezone.now().isoformat(),
                }
            )
        else:
            await self.send_error("Failed to mark message as read")

    async def handle_typing_start(self):
        """
        Handle user started typing event.
        
        Broadcasts typing indicator to other conversation participants.
        """
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                "type": "user_typing",
                "user_id": self.user.id,
                "username": self.user.get_full_name(),
                "is_typing": True,
            }
        )

    async def handle_typing_stop(self):
        """
        Handle user stopped typing event.
        
        Broadcasts stop typing indicator to other conversation participants.
        """
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                "type": "user_typing",
                "user_id": self.user.id,
                "username": self.user.get_full_name(),
                "is_typing": False,
            }
        )

    # Event handlers for channel layer messages
    async def chat_message(self, event):
        """
        Handle chat_message event from channel layer.
        
        Sends message to WebSocket client.
        
        Args:
            event (dict): Event data from channel layer
        """
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "id": event["message_id"],
            "content": event["content"],
            "sender": event["sender"],
            "created_at": event["created_at"],
            "is_read": event["is_read"],
        }))

    async def message_read(self, event):
        """
        Handle message_read event from channel layer.
        
        Sends read receipt to WebSocket client.
        
        Args:
            event (dict): Event data from channel layer
        """
        await self.send(text_data=json.dumps({
            "type": "message_read",
            "message_id": event["message_id"],
            "read_by_user_id": event["read_by_user_id"],
            "read_at": event["read_at"],
        }))

    async def user_typing(self, event):
        """
        Handle user_typing event from channel layer.
        
        Sends typing indicator to WebSocket client (excluding sender).
        
        Args:
            event (dict): Event data from channel layer
        """
        # Don't send typing indicator back to the typer
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "user_typing",
                "user_id": event["user_id"],
                "username": event["username"],
                "is_typing": event["is_typing"],
            }))

    async def user_status(self, event):
        """
        Handle user_status event from channel layer.
        
        Sends online/offline status to WebSocket client (excluding sender).
        
        Args:
            event (dict): Event data from channel layer
        """
        # Don't send status back to the user themselves
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "user_status",
                "user_id": event["user_id"],
                "username": event["username"],
                "status": event["status"],
            }))

    async def send_error(self, error_message):
        """
        Send error message to WebSocket client.
        
        Args:
            error_message (str): Error description
        """
        await self.send(text_data=json.dumps({
            "type": "error",
            "error": error_message,
        }))

    # Database operations (async wrappers)
    @database_sync_to_async
    def get_conversation(self):
        """
        Retrieve conversation from database.
        
        Returns:
            Conversation: The conversation instance
        
        Raises:
            Conversation.DoesNotExist: If conversation not found
        """
        return Conversation.objects.get(id=self.conversation_id)

    @database_sync_to_async
    def is_participant(self):
        """
        Check if current user is a conversation participant.
        
        Returns:
            bool: True if user is a participant, False otherwise
        """
        participants = self.conversation.get_participants()
        return self.user in participants

    @database_sync_to_async
    def save_message(self, content):
        """
        Save new message to database.
        
        Args:
            content (str): Message content
        
        Returns:
            ChatMessage: The created message instance
        """
        return ChatMessage.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content=content,
        )

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """
        Mark message as read in database.
        
        Args:
            message_id (str): UUID of the message
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message = ChatMessage.objects.get(
                id=message_id,
                conversation=self.conversation,
            )
            message.mark_as_read()
            return True
        except ChatMessage.DoesNotExist:
            return False
