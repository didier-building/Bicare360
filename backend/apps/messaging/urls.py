"""URL configuration for the messaging app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.messaging.views import (
    MessageTemplateViewSet,
    MessageViewSet,
    MessageLogViewSet,
    MessageQueueViewSet,
)

app_name = "messaging"

router = DefaultRouter()
router.register(r"message-templates", MessageTemplateViewSet, basename="messagetemplate")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r"message-logs", MessageLogViewSet, basename="messagelog")
router.register(r"message-queue", MessageQueueViewSet, basename="messagequeue")

urlpatterns = [
    path("", include(router.urls)),
]
