"""Models for the messaging app."""

from django.db import models
from django.utils import timezone


class MessageTemplate(models.Model):
    """
    Message templates for different notification types.
    
    Supports bilingual content (English and Kinyarwanda) and different
    message types (SMS, WhatsApp).
    """

    TEMPLATE_TYPE_CHOICES = [
        ("appointment_reminder", "Appointment Reminder"),
        ("medication_reminder", "Medication Reminder"),
        ("general_notification", "General Notification"),
        ("emergency_alert", "Emergency Alert"),
        ("survey", "Survey"),
    ]

    MESSAGE_TYPE_CHOICES = [
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Unique template identifier")
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    content_english = models.TextField(help_text="Message content in English with placeholders {variable_name}")
    content_kinyarwanda = models.TextField(
        blank=True, null=True, help_text="Message content in Kinyarwanda with placeholders"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this template is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for MessageTemplate."""

        ordering = ["name"]
        indexes = [
            models.Index(fields=["template_type", "message_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        """Return string representation."""
        return f"{self.name} ({self.message_type})"


class Message(models.Model):
    """
    Individual messages sent to patients.
    
    Tracks message delivery status and links to appointments and templates.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    MESSAGE_TYPE_CHOICES = [
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
    ]

    recipient_patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE, related_name="messages"
    )
    recipient_phone = models.CharField(max_length=20, help_text="Phone number with country code")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    content = models.TextField(help_text="Final rendered message content")
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messages",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    scheduled_send_time = models.DateTimeField(
        null=True, blank=True, help_text="When to send the message"
    )
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When message was actually sent")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Message."""

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient_patient", "status"]),
            models.Index(fields=["status", "scheduled_send_time"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        """Return string representation."""
        return f"{self.recipient_patient.full_name} - {self.message_type} - {self.status}"


class MessageLog(models.Model):
    """
    Detailed logs of message delivery attempts.
    
    Records provider responses, costs, and delivery status for audit trail.
    """

    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("rejected", "Rejected"),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    provider_message_id = models.CharField(
        max_length=100, null=True, blank=True, help_text="Message ID from Africa's Talking"
    )
    provider_response = models.TextField(
        null=True, blank=True, help_text="Full response from Africa's Talking API"
    )
    error_message = models.TextField(null=True, blank=True, help_text="Error details if delivery failed")
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True, help_text="Cost of sending the message"
    )
    currency = models.CharField(max_length=3, default="USD", help_text="Currency code (USD, RWF, etc.)")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for MessageLog."""

        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["message", "-timestamp"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        """Return string representation."""
        return f"Log for {self.message.recipient_patient.full_name} - {self.status} at {self.timestamp}"


class MessageQueue(models.Model):
    """
    Queue for scheduled message delivery.
    
    Manages pending messages with priority and retry logic.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    MESSAGE_TYPE_CHOICES = [
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
    ]

    recipient_phone = models.CharField(max_length=20)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    scheduled_time = models.DateTimeField(help_text="When to send this message")
    template_name = models.CharField(max_length=100, null=True, blank=True)
    context_data = models.JSONField(null=True, blank=True, help_text="Template variables for rendering")
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="queued_messages",
    )
    sent_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queue_entry",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="normal")
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for MessageQueue."""

        ordering = ["-priority", "scheduled_time"]
        indexes = [
            models.Index(fields=["status", "scheduled_time"]),
            models.Index(fields=["priority", "scheduled_time"]),
            models.Index(fields=["appointment"]),
        ]

    def __str__(self):
        """Return string representation."""
        return f"{self.recipient_phone} - {self.message_type} - {self.priority} priority"
