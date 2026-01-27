"""Serializers for the messaging app."""

from rest_framework import serializers
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue
from apps.patients.serializers import PatientListSerializer


class MessageTemplateSerializer(serializers.ModelSerializer):
    """Serializer for MessageTemplate model."""

    class Meta:
        model = MessageTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "message_type",
            "content_english",
            "content_kinyarwanda",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class MessageSerializer(serializers.ModelSerializer):
    """Basic serializer for Message model."""

    class Meta:
        model = Message
        fields = [
            "id",
            "recipient_patient",
            "recipient_phone",
            "message_type",
            "template",
            "content",
            "appointment",
            "status",
            "scheduled_send_time",
            "sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class MessageListSerializer(serializers.ModelSerializer):
    """Optimized serializer for message list views."""

    patient_name = serializers.SerializerMethodField()
    template_name = serializers.CharField(source="template.name", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "patient_name",
            "recipient_phone",
            "message_type",
            "template_name",
            "status",
            "scheduled_send_time",
            "sent_at",
            "created_at",
        ]
    
    def get_patient_name(self, obj):
        """Get patient full name."""
        if obj.recipient_patient:
            return f"{obj.recipient_patient.first_name} {obj.recipient_patient.last_name}"
        return None


class MessageDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested relationships."""

    patient = PatientListSerializer(source="recipient_patient", read_only=True)
    template = MessageTemplateSerializer(read_only=True)
    appointment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "patient",
            "recipient_phone",
            "message_type",
            "template",
            "content",
            "appointment",
            "status",
            "scheduled_send_time",
            "sent_at",
            "created_at",
            "updated_at",
        ]


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""

    class Meta:
        model = Message
        fields = [
            "recipient_patient",
            "recipient_phone",
            "message_type",
            "template",
            "content",
            "appointment",
            "status",
            "scheduled_send_time",
        ]


class MessageLogSerializer(serializers.ModelSerializer):
    """Serializer for MessageLog model (read-only)."""

    class Meta:
        model = MessageLog
        fields = [
            "id",
            "message",
            "status",
            "provider_message_id",
            "provider_response",
            "error_message",
            "cost",
            "currency",
            "timestamp",
        ]
        read_only_fields = fields  # All fields are read-only


class MessageQueueSerializer(serializers.ModelSerializer):
    """Serializer for MessageQueue model."""

    class Meta:
        model = MessageQueue
        fields = [
            "id",
            "recipient_phone",
            "message_type",
            "content",
            "scheduled_time",
            "template_name",
            "context_data",
            "appointment",
            "sent_message",
            "status",
            "priority",
            "retry_count",
            "max_retries",
            "processed_at",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "processed_at"]
