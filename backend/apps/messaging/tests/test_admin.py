"""Tests for messaging admin interface."""
import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory
from unittest.mock import Mock, patch

from apps.messaging.admin import (
    MessageTemplateAdmin,
    MessageAdmin,
    MessageLogAdmin,
    MessageQueueAdmin,
)
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue
from apps.messaging.tests.factories import (
    MessageTemplateFactory,
    MessageFactory,
    MessageLogFactory,
    MessageQueueFactory,
    PatientFactory,
)


pytestmark = pytest.mark.django_db


class TestMessageTemplateAdmin:
    """Test MessageTemplateAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = MessageTemplateAdmin(MessageTemplate, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')

    def test_list_display(self):
        """Test list_display configuration."""
        assert 'name' in self.admin.list_display
        assert 'template_type' in self.admin.list_display
        assert 'message_type' in self.admin.list_display
        assert 'is_active' in self.admin.list_display

    def test_list_filter(self):
        """Test list_filter configuration."""
        assert 'template_type' in self.admin.list_filter
        assert 'message_type' in self.admin.list_filter
        assert 'is_active' in self.admin.list_filter

    def test_search_fields(self):
        """Test search_fields configuration."""
        assert 'name' in self.admin.search_fields
        assert 'content_english' in self.admin.search_fields
        assert 'content_kinyarwanda' in self.admin.search_fields

    def test_message_count_display(self):
        """Test message_count display method."""
        template = MessageTemplateFactory()
        MessageFactory(template=template)
        MessageFactory(template=template)
        
        result = self.admin.message_count(template)
        assert '2' in str(result)


class TestMessageAdmin:
    """Test MessageAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = MessageAdmin(Message, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')

    def test_list_display(self):
        """Test list_display configuration."""
        assert 'recipient_phone' in self.admin.list_display
        assert 'message_type' in self.admin.list_display
        assert 'status_display' in self.admin.list_display
        assert 'recipient_display' in self.admin.list_display

    def test_list_filter(self):
        """Test list_filter configuration."""
        assert 'status' in self.admin.list_filter
        assert 'message_type' in self.admin.list_filter
        assert 'created_at' in self.admin.list_filter

    def test_search_fields(self):
        """Test search_fields configuration."""
        assert 'recipient_phone' in self.admin.search_fields
        assert 'content' in self.admin.search_fields

    def test_mark_as_sent_action(self):
        """Test mark as sent action."""
        message1 = MessageFactory(status="pending", message_type="sms")
        message2 = MessageFactory(status="pending", message_type="sms")
        
        request = self.factory.get('/')
        request.user = self.user
        request._messages = Mock()
        
        queryset = Message.objects.filter(id__in=[message1.id, message2.id])
        self.admin.mark_as_sent(request, queryset)
        
        message1.refresh_from_db()
        message2.refresh_from_db()
        
        assert message1.status == "sent"
        assert message2.status == "sent"
        assert message1.sent_at is not None
        assert message2.sent_at is not None

    def test_mark_as_failed_action(self):
        """Test mark as failed action."""
        message1 = MessageFactory(status="pending", message_type="sms")
        message2 = MessageFactory(status="queued", message_type="sms")
        
        request = self.factory.get('/')
        request.user = self.user
        request._messages = Mock()
        
        queryset = Message.objects.filter(id__in=[message1.id, message2.id])
        self.admin.mark_as_failed(request, queryset)
        
        message1.refresh_from_db()
        message2.refresh_from_db()
        
        assert message1.status == "failed"
        assert message2.status == "failed"

    def test_mark_as_cancelled_action(self):
        """Test mark as cancelled action."""
        message1 = MessageFactory(status="pending")
        message2 = MessageFactory(status="queued")
        
        request = self.factory.get('/')
        request.user = self.user
        request._messages = Mock()
        
        queryset = Message.objects.filter(id__in=[message1.id, message2.id])
        self.admin.mark_as_cancelled(request, queryset)
        
        message1.refresh_from_db()
        message2.refresh_from_db()
        
        assert message1.status == "cancelled"
        assert message2.status == "cancelled"


class TestMessageLogAdmin:
    """Test MessageLogAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = MessageLogAdmin(MessageLog, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')

    def test_list_display(self):
        """Test list_display configuration."""
        assert 'message_display' in self.admin.list_display
        assert 'status_display' in self.admin.list_display
        assert 'provider_message_id' in self.admin.list_display
        assert 'cost' in self.admin.list_display
        assert 'timestamp' in self.admin.list_display

    def test_list_filter(self):
        """Test list_filter configuration."""
        assert 'status' in self.admin.list_filter
        assert 'timestamp' in self.admin.list_filter

    def test_search_fields(self):
        """Test search_fields configuration."""
        assert 'provider_message_id' in self.admin.search_fields

    def test_readonly_fields(self):
        """Test readonly_fields configuration."""
        assert 'message' in self.admin.readonly_fields
        assert 'status' in self.admin.readonly_fields
        assert 'provider_message_id' in self.admin.readonly_fields

    def test_has_add_permission(self):
        """Test that logs cannot be added manually."""
        request = self.factory.get('/')
        request.user = self.user
        
        assert self.admin.has_add_permission(request) is False

    def test_has_delete_permission(self):
        """Test that logs cannot be deleted."""
        request = self.factory.get('/')
        request.user = self.user
        
        assert self.admin.has_delete_permission(request) is False


class TestMessageQueueAdmin:
    """Test MessageQueueAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = MessageQueueAdmin(MessageQueue, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')

    def test_list_display(self):
        """Test list_display configuration."""
        assert 'recipient_phone' in self.admin.list_display
        assert 'scheduled_time' in self.admin.list_display
        assert 'priority_display' in self.admin.list_display
        assert 'status_display' in self.admin.list_display

    def test_list_filter(self):
        """Test list_filter configuration."""
        assert 'status' in self.admin.list_filter
        assert 'priority' in self.admin.list_filter
        assert 'scheduled_time' in self.admin.list_filter

    def test_search_fields(self):
        """Test search_fields configuration."""
        assert 'recipient_phone' in self.admin.search_fields

    def test_process_now_action(self):
        """Test process now action."""
        from django.utils import timezone
        patient = PatientFactory()
        # Create pending entry with past scheduled time
        entry1 = MessageQueueFactory(
            status="pending",
            recipient_phone=patient.phone_number,
            scheduled_time=timezone.now() - timezone.timedelta(hours=1)
        )
        entry2 = MessageQueueFactory(
            status="pending",
            recipient_phone=patient.phone_number,
            scheduled_time=timezone.now() - timezone.timedelta(minutes=30)
        )
        
        request = self.factory.get('/')
        request.user = self.user
        request._messages = Mock()
        
        queryset = MessageQueue.objects.filter(id__in=[entry1.id, entry2.id])
        self.admin.process_now(request, queryset)
        
        entry1.refresh_from_db()
        entry2.refresh_from_db()
        
        assert entry1.status == "processing"
        assert entry2.status == "processing"

    def test_cancel_pending_action(self):
        """Test cancel pending action."""
        patient = PatientFactory()
        entry1 = MessageQueueFactory(status="pending", recipient_phone=patient.phone_number)
        entry2 = MessageQueueFactory(status="pending", recipient_phone=patient.phone_number)
        
        request = self.factory.get('/')
        request.user = self.user
        request._messages = Mock()
        
        queryset = MessageQueue.objects.filter(id__in=[entry1.id, entry2.id])
        self.admin.cancel_pending(request, queryset)
        
        entry1.refresh_from_db()
        entry2.refresh_from_db()
        
        assert entry1.status == "cancelled"
        assert entry2.status == "cancelled"

    def test_reset_for_retry_action(self):
        """Test reset for retry action."""
        patient = PatientFactory()
        entry1 = MessageQueueFactory(
            status="failed",
            recipient_phone=patient.phone_number,
            error_message="Some error"
        )
        entry2 = MessageQueueFactory(
            status="failed",
            recipient_phone=patient.phone_number,
            error_message="Another error"
        )
        
        request = self.factory.get('/')
        request.user = self.user
        request._messages = Mock()
        
        queryset = MessageQueue.objects.filter(id__in=[entry1.id, entry2.id])
        self.admin.reset_for_retry(request, queryset)
        
        entry1.refresh_from_db()
        entry2.refresh_from_db()
        
        assert entry1.status == "pending"
        assert entry2.status == "pending"
        assert entry1.error_message is None
        assert entry2.error_message is None
