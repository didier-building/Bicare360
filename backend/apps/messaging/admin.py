"""Admin configuration for the messaging app."""

from django.contrib import admin
from django.utils.html import format_html
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    """Admin interface for MessageTemplate model."""

    list_display = [
        "name",
        "template_type",
        "message_type",
        "is_active",
        "created_at",
        "message_count",
    ]
    list_filter = ["template_type", "message_type", "is_active", "created_at"]
    search_fields = ["name", "content_english", "content_kinyarwanda"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    ordering = ["name"]

    fieldsets = (
        (
            "Template Information",
            {
                "fields": (
                    "name",
                    "template_type",
                    "message_type",
                    "is_active",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "content_english",
                    "content_kinyarwanda",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def message_count(self, obj):
        """Display the number of messages using this template."""
        count = obj.messages.count()
        return format_html('<strong>{}</strong>', count)

    message_count.short_description = "Messages Sent"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = [
        "id",
        "recipient_display",
        "recipient_phone",
        "message_type",
        "status_display",
        "sent_at",
        "created_at",
    ]
    list_filter = ["status", "message_type", "created_at", "sent_at"]
    search_fields = [
        "recipient_phone",
        "content",
        "recipient_patient__first_name",
        "recipient_patient__last_name",
        "recipient_patient__national_id",
    ]
    readonly_fields = ["created_at", "updated_at", "sent_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    autocomplete_fields = ["recipient_patient", "template", "appointment"]
    raw_id_fields = ["recipient_patient", "template", "appointment"]

    fieldsets = (
        (
            "Recipient Information",
            {
                "fields": (
                    "recipient_patient",
                    "recipient_phone",
                )
            },
        ),
        (
            "Message Details",
            {
                "fields": (
                    "message_type",
                    "template",
                    "content",
                    "appointment",
                )
            },
        ),
        (
            "Status & Timing",
            {
                "fields": (
                    "status",
                    "scheduled_send_time",
                    "sent_at",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def recipient_display(self, obj):
        """Display recipient patient name."""
        if obj.recipient_patient:
            return obj.recipient_patient.full_name
        return "N/A"

    recipient_display.short_description = "Patient"

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            "pending": "orange",
            "queued": "blue",
            "sent": "green",
            "delivered": "darkgreen",
            "failed": "red",
            "cancelled": "gray",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    actions = ["mark_as_sent", "mark_as_failed", "mark_as_cancelled"]

    def mark_as_sent(self, request, queryset):
        """Mark selected messages as sent."""
        from django.utils import timezone
        updated = queryset.filter(status="pending").update(status="sent", sent_at=timezone.now())
        self.message_user(request, f"{updated} message(s) marked as sent.")

    mark_as_sent.short_description = "Mark selected as sent"

    def mark_as_failed(self, request, queryset):
        """Mark selected messages as failed."""
        updated = queryset.filter(status__in=["pending", "queued"]).update(status="failed")
        self.message_user(request, f"{updated} message(s) marked as failed.")

    mark_as_failed.short_description = "Mark selected as failed"

    def mark_as_cancelled(self, request, queryset):
        """Mark selected messages as cancelled."""
        updated = queryset.filter(status__in=["pending", "queued"]).update(status="cancelled")
        self.message_user(request, f"{updated} message(s) marked as cancelled.")

    mark_as_cancelled.short_description = "Mark selected as cancelled"


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    """Admin interface for MessageLog model (read-only)."""

    list_display = [
        "id",
        "message_display",
        "status_display",
        "provider_message_id",
        "cost",
        "currency",
        "timestamp",
    ]
    list_filter = ["status", "currency", "timestamp"]
    search_fields = [
        "provider_message_id",
        "message__recipient_phone",
        "message__recipient_patient__first_name",
        "message__recipient_patient__last_name",
    ]
    readonly_fields = [
        "message",
        "status",
        "provider_message_id",
        "provider_response",
        "error_message",
        "cost",
        "currency",
        "timestamp",
    ]
    date_hierarchy = "timestamp"
    ordering = ["-timestamp"]
    raw_id_fields = ["message"]

    fieldsets = (
        (
            "Message & Status",
            {
                "fields": (
                    "message",
                    "status",
                )
            },
        ),
        (
            "Provider Information",
            {
                "fields": (
                    "provider_message_id",
                    "provider_response",
                    "error_message",
                )
            },
        ),
        (
            "Cost",
            {
                "fields": (
                    "cost",
                    "currency",
                )
            },
        ),
        (
            "Timestamp",
            {
                "fields": ("timestamp",)
            },
        ),
    )

    def has_add_permission(self, request):
        """Logs are created automatically, not manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Logs are read-only."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Logs should not be deleted (audit trail)."""
        return False

    def message_display(self, obj):
        """Display message recipient."""
        return f"{obj.message.recipient_phone}"

    message_display.short_description = "Message To"

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            "queued": "blue",
            "sent": "green",
            "delivered": "darkgreen",
            "failed": "red",
            "rejected": "darkred",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"


@admin.register(MessageQueue)
class MessageQueueAdmin(admin.ModelAdmin):
    """Admin interface for MessageQueue model."""

    list_display = [
        "id",
        "recipient_phone",
        "message_type",
        "priority_display",
        "status_display",
        "scheduled_time",
        "retry_count",
        "processed_at",
    ]
    list_filter = ["status", "priority", "message_type", "scheduled_time", "processed_at"]
    search_fields = [
        "recipient_phone",
        "content",
        "template_name",
    ]
    readonly_fields = ["sent_message", "processed_at", "created_at", "updated_at"]
    date_hierarchy = "scheduled_time"
    ordering = ["-priority", "scheduled_time"]
    autocomplete_fields = ["appointment"]
    raw_id_fields = ["appointment", "sent_message"]

    fieldsets = (
        (
            "Recipient & Content",
            {
                "fields": (
                    "recipient_phone",
                    "message_type",
                    "content",
                )
            },
        ),
        (
            "Template",
            {
                "fields": (
                    "template_name",
                    "context_data",
                )
            },
        ),
        (
            "Scheduling",
            {
                "fields": (
                    "scheduled_time",
                    "priority",
                    "status",
                )
            },
        ),
        (
            "Retry Logic",
            {
                "fields": (
                    "retry_count",
                    "max_retries",
                    "error_message",
                )
            },
        ),
        (
            "References",
            {
                "fields": (
                    "appointment",
                    "sent_message",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "processed_at",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def priority_display(self, obj):
        """Display priority with visual emphasis."""
        colors = {
            "low": "gray",
            "normal": "blue",
            "high": "orange",
            "urgent": "red",
        }
        color = colors.get(obj.priority, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display().upper(),
        )

    priority_display.short_description = "Priority"

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            "pending": "orange",
            "processing": "blue",
            "completed": "green",
            "failed": "red",
            "cancelled": "gray",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    actions = ["process_now", "cancel_pending", "reset_for_retry"]

    def process_now(self, request, queryset):
        """Process selected pending entries."""
        from django.utils import timezone
        updated = queryset.filter(status="pending", scheduled_time__lte=timezone.now()).update(
            status="processing"
        )
        self.message_user(request, f"{updated} queue entry(ies) marked for processing.")

    process_now.short_description = "Process now (if scheduled)"

    def cancel_pending(self, request, queryset):
        """Cancel selected pending entries."""
        updated = queryset.filter(status="pending").update(status="cancelled")
        self.message_user(request, f"{updated} queue entry(ies) cancelled.")

    cancel_pending.short_description = "Cancel pending"

    def reset_for_retry(self, request, queryset):
        """Reset failed entries for retry."""
        updated = queryset.filter(status="failed").update(
            status="pending", error_message=None
        )
        self.message_user(request, f"{updated} failed entry(ies) reset for retry.")

    reset_for_retry.short_description = "Reset failed for retry"
