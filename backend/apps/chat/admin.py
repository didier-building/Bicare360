"""
Django Admin Configuration for BiCare360 Chat Models

This module registers chat models with the Django admin interface,
providing administrative access to conversations, messages, and attachments.

Admin Interface Features:
- List display with key information
- Search and filter capabilities
- Read-only fields for security
- Inline editing for related objects
- Custom actions for bulk operations

Author: Didier IMANIRAHARI
Date: February 2026
"""

from django.contrib import admin
from django.utils.html import format_html

from apps.chat.models import ChatMessage, Conversation, MessageAttachment


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin interface for Conversation model.
    
    Provides:
    - List display of conversations with participants
    - Filtering by participant type and date
    - Search by participant names
    - Read-only timestamps
    """
    
    list_display = [
        "id",
        "get_participants_display",
        "created_at",
        "updated_at",
        "message_count",
    ]
    
    list_filter = [
        "created_at",
        "updated_at",
    ]
    
    search_fields = [
        "patient__user__first_name",
        "patient__user__last_name",
        "caregiver__user__first_name",
        "caregiver__user__last_name",
        "nurse__user__first_name",
        "nurse__user__last_name",
    ]
    
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "get_participants_display",
        "message_count",
    ]
    
    date_hierarchy = "created_at"
    
    def get_participants_display(self, obj):
        """Display conversation participants."""
        return str(obj)
    
    get_participants_display.short_description = "Participants"
    
    def message_count(self, obj):
        """Display count of messages in conversation."""
        count = obj.messages.filter(is_deleted=False).count()
        return format_html('<strong>{}</strong> messages', count)
    
    message_count.short_description = "Messages"


class MessageAttachmentInline(admin.TabularInline):
    """Inline admin for message attachments."""
    
    model = MessageAttachment
    extra = 0
    readonly_fields = ["file", "file_name", "file_size", "file_type", "uploaded_at"]
    can_delete = False


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for ChatMessage model.
    
    Provides:
    - List display of messages with sender and status
    - Filtering by read status, deleted status, and date
    - Search by content and sender
    - Inline attachment display
    - Actions for bulk operations
    """
    
    list_display = [
        "id",
        "conversation",
        "sender",
        "content_preview",
        "is_read",
        "is_deleted",
        "created_at",
    ]
    
    list_filter = [
        "is_read",
        "is_deleted",
        "created_at",
    ]
    
    search_fields = [
        "content",
        "sender__first_name",
        "sender__last_name",
        "sender__email",
    ]
    
    readonly_fields = [
        "id",
        "conversation",
        "sender",
        "created_at",
        "updated_at",
        "read_at",
    ]
    
    date_hierarchy = "created_at"
    
    inlines = [MessageAttachmentInline]
    
    actions = ["mark_as_read", "mark_as_deleted"]
    
    def content_preview(self, obj):
        """Display truncated message content."""
        max_length = 50
        if len(obj.content) > max_length:
            return obj.content[:max_length] + "..."
        return obj.content
    
    content_preview.short_description = "Content"
    
    def mark_as_read(self, request, queryset):
        """Bulk action to mark messages as read."""
        count = 0
        for message in queryset:
            if not message.is_read:
                message.mark_as_read()
                count += 1
        self.message_user(request, f"{count} message(s) marked as read.")
    
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_deleted(self, request, queryset):
        """Bulk action to soft delete messages."""
        count = 0
        for message in queryset:
            if not message.is_deleted:
                message.soft_delete()
                count += 1
        self.message_user(request, f"{count} message(s) marked as deleted.")
    
    mark_as_deleted.short_description = "Soft delete selected messages"


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    """
    Admin interface for MessageAttachment model.
    
    Provides:
    - List display of attachments with file info
    - Filtering by file type and upload date
    - Search by filename
    - Read-only file fields
    """
    
    list_display = [
        "id",
        "message",
        "file_name",
        "file_size_display",
        "file_type",
        "uploaded_at",
    ]
    
    list_filter = [
        "file_type",
        "uploaded_at",
    ]
    
    search_fields = [
        "file_name",
    ]
    
    readonly_fields = [
        "id",
        "message",
        "file",
        "file_name",
        "file_size",
        "file_type",
        "uploaded_at",
        "file_size_display",
    ]
    
    date_hierarchy = "uploaded_at"
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        size_kb = obj.file_size / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} KB"
        else:
            size_mb = size_kb / 1024
            return f"{size_mb:.2f} MB"
    
    file_size_display.short_description = "File Size"
