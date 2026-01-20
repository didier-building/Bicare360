"""Views for the messaging app."""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Count
from apps.messaging.models import MessageTemplate, Message, MessageLog, MessageQueue
from apps.messaging.serializers import (
    MessageTemplateSerializer,
    MessageSerializer,
    MessageListSerializer,
    MessageDetailSerializer,
    MessageCreateSerializer,
    MessageLogSerializer,
    MessageQueueSerializer,
)
from apps.messaging.tasks import send_message_task, process_message_queue, send_bulk_messages
from apps.messaging.tasks import send_message_task, send_bulk_messages, schedule_appointment_reminders
from apps.messaging.analytics import MessageAnalytics
from apps.messaging.sms_service import MessageService
from apps.core.permissions import IsAuthenticatedUser


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for MessageTemplate model."""

    queryset = MessageTemplate.objects.all()
    serializer_class = MessageTemplateSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["template_type", "message_type", "is_active"]
    search_fields = ["name", "content_english", "content_kinyarwanda"]
    ordering_fields = ["name", "created_at", "template_type"]
    ordering = ["name"]

    @action(detail=False, methods=["get"])
    def usage_stats(self, request):
        """Get usage statistics for templates."""
        stats = (
            MessageTemplate.objects.annotate(usage_count=Count("messages"))
            .values("id", "name", "usage_count")
            .order_by("-usage_count")
        )
        return Response(list(stats))


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model."""

    queryset = Message.objects.all().select_related("recipient_patient", "template", "appointment")
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "message_type", "recipient_patient", "template"]
    search_fields = ["content", "recipient_phone", "recipient_patient__first_name", "recipient_patient__last_name"]
    ordering_fields = ["created_at", "sent_at", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == "list":
            return MessageListSerializer
        elif self.action == "retrieve":
            return MessageDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return MessageCreateSerializer
        return MessageSerializer

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """Send a queued message asynchronously."""
        message = self.get_object()
        
        if message.status not in ["pending", "queued", "failed"]:
            return Response(
                {"error": "Message has already been processed or is being sent"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status to queued
        message.status = "queued"
        message.save()
        
        # Trigger async send task
        task = send_message_task.delay(message.id)
        
        return Response({
            "message": "Message queued for sending",
            "message_id": message.id,
            "task_id": task.id,
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get message statistics."""
        total_messages = Message.objects.count()
        by_status = dict(Message.objects.values("status").annotate(count=Count("id")).values_list("status", "count"))
        by_type = dict(Message.objects.values("message_type").annotate(count=Count("id")).values_list("message_type", "count"))
        
        return Response({
            "total_messages": total_messages,
            "by_status": by_status,
            "by_type": by_type,
        })

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get comprehensive message analytics."""
        days = int(request.query_params.get('days', 7))
        
        analytics = MessageAnalytics()
        
        return Response({
            "delivery_stats": analytics.get_delivery_stats(days=days),
            "channel_breakdown": analytics.get_channel_breakdown(days=days),
            "template_usage": analytics.get_template_usage(days=30),
        })

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Get dashboard summary with key metrics."""
        analytics = MessageAnalytics()
        return Response(analytics.get_dashboard_summary())

    @action(detail=False, methods=["get"])
    def failed_messages(self, request):
        """Get list of failed messages for retry."""
        limit = int(request.query_params.get('limit', 50))
        analytics = MessageAnalytics()
        
        return Response({
            "failed_messages": analytics.get_failed_messages(limit=limit),
            "total_count": Message.objects.filter(status='failed').count()
        })

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """Retry sending a failed message."""
        message = self.get_object()
        
        if message.status not in ['failed', 'cancelled']:
            return Response(
                {"error": "Only failed or cancelled messages can be retried"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset message status
        message.status = 'pending'
        message.save()
        
        # Send via message service
        service = MessageService()
        success = service.send_message(message.id)
        
        return Response({
            "success": success,
            "message_id": message.id,
            "new_status": message.status
        })

    @action(detail=False, methods=["post"])
    def retry_all_failed(self, request):
        """Retry all failed messages."""
        limit = int(request.data.get('limit', 10))
        
        failed_messages = Message.objects.filter(status='failed').order_by('-created_at')[:limit]
        
        service = MessageService()
        results = []
        
        for message in failed_messages:
            message.status = 'pending'
            message.save()
            success = service.send_message(message.id)
            results.append({
                "message_id": message.id,
                "success": success
            })
        
        return Response({
            "attempted": len(results),
            "results": results
        })

    @action(detail=False, methods=["get"])
    def hourly_volume(self, request):
        """Get message volume by hour."""
        days = int(request.query_params.get('days', 1))
        analytics = MessageAnalytics()
        
        return Response(analytics.get_hourly_volume(days=days))

    @action(detail=False, methods=["get"])
    def patient_history(self, request):
        """Get message history for a specific patient."""
        patient_id = request.query_params.get('patient_id')
        
        if not patient_id:
            return Response(
                {"error": "patient_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        limit = int(request.query_params.get('limit', 20))
        analytics = MessageAnalytics()
        
        return Response({
            "patient_id": patient_id,
            "messages": analytics.get_patient_message_history(int(patient_id), limit=limit)
        })

    @action(detail=False, methods=["post"])
    def send_bulk(self, request):
        """Send messages to multiple recipients asynchronously."""
        recipients = request.data.get("recipients", [])
        message_type = request.data.get("message_type")
        template_id = request.data.get("template")
        content = request.data.get("content")
        
        if not recipients or not message_type or not content:
            return Response(
                {"error": "recipients, message_type, and content are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger async bulk send task
        task = send_bulk_messages.delay(
            recipients=recipients,
            message_type=message_type,
            content=content,
            template_id=template_id
        )
        
        return Response({
            "message": "Bulk messages queued for sending",
            "recipient_count": len(recipients),
            "task_id": task.id,
        })


class MessageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MessageLog model (read-only)."""

    queryset = MessageLog.objects.all().select_related("message")
    serializer_class = MessageLogSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "message"]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]


class MessageQueueViewSet(viewsets.ModelViewSet):
    """ViewSet for MessageQueue model."""

    queryset = MessageQueue.objects.all().select_related("appointment", "sent_message")
    serializer_class = MessageQueueSerializer
    permission_classes = [IsAuthenticatedUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "message_type", "appointment"]
    ordering_fields = ["scheduled_time", "priority", "created_at"]
    ordering = ["-priority", "scheduled_time"]

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        """Process a pending queue entry."""
        entry = self.get_object()
        
        if entry.status != "pending":
            return Response(
                {"error": "Entry is not pending"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if scheduled time has passed
        if entry.scheduled_time > timezone.now():
            return Response(
                {"error": "Scheduled time has not arrived yet"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Integrate with actual messaging service
        # For now, simulate processing
        entry.status = "processing"
        entry.save()
        
        # Create message
        message = Message.objects.create(
            recipient_patient_id=entry.appointment.patient_id if entry.appointment else None,
            recipient_phone=entry.recipient_phone,
            message_type=entry.message_type,
            content=entry.content,
            status="sent",
            sent_at=timezone.now(),
        )
        
        entry.sent_message = message
        entry.status = "completed"
        entry.processed_at = timezone.now()
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """Retry a failed queue entry."""
        entry = self.get_object()
        
        if entry.status != "failed":
            return Response(
                {"error": "Entry is not failed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if entry.retry_count >= entry.max_retries:
            return Response(
                {"error": "Maximum retries reached"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        entry.retry_count += 1
        entry.status = "pending"
        entry.error_message = None
        entry.save()
        
        serializer = self.get_serializer(entry)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def schedule_reminders(self, request):
        """Schedule bulk appointment reminders asynchronously."""
        appointment_ids = request.data.get("appointments", [])
        reminder_times = request.data.get("reminder_times", ["24h", "2h"])
        
        if not appointment_ids:
            return Response(
                {"error": "appointments list is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger async reminder scheduling task
        task = schedule_appointment_reminders.delay(
            appointment_ids=appointment_ids,
            reminder_times=reminder_times
        )
        
        return Response({
            "message": "Appointment reminders scheduled",
            "appointment_count": len(appointment_ids),
            "reminder_times": reminder_times,
            "task_id": task.id,
        })
