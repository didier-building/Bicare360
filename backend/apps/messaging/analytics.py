"""
Message analytics and reporting services.
"""
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List
from .models import Message, MessageLog, MessageTemplate


class MessageAnalytics:
    """Service for message analytics and reporting."""

    @staticmethod
    def get_delivery_stats(days: int = 7) -> Dict:
        """
        Get message delivery statistics for the past N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with delivery statistics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Get message counts by status
        messages = Message.objects.filter(created_at__gte=start_date)
        
        stats = messages.aggregate(
            total=Count('id'),
            sent=Count('id', filter=Q(status='sent')),
            delivered=Count('id', filter=Q(status='delivered')),
            failed=Count('id', filter=Q(status='failed')),
            pending=Count('id', filter=Q(status='pending')),
            queued=Count('id', filter=Q(status='queued')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        )
        
        # Calculate rates
        total = stats['total'] or 1  # Avoid division by zero
        stats['success_rate'] = round((stats['sent'] + stats['delivered']) / total * 100, 2)
        stats['failure_rate'] = round(stats['failed'] / total * 100, 2)
        
        return stats

    @staticmethod
    def get_channel_breakdown(days: int = 7) -> Dict:
        """
        Get breakdown of messages by channel (SMS, WhatsApp, Email).
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with channel statistics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        messages = Message.objects.filter(created_at__gte=start_date)
        
        breakdown = messages.values('message_type').annotate(
            total=Count('id'),
            sent=Count('id', filter=Q(status='sent')),
            failed=Count('id', filter=Q(status='failed'))
        )
        
        return {
            'channels': list(breakdown),
            'period_days': days
        }

    @staticmethod
    def get_template_usage(days: int = 30) -> List[Dict]:
        """
        Get template usage statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of template usage stats
        """
        start_date = timezone.now() - timedelta(days=days)
        
        usage = Message.objects.filter(
            created_at__gte=start_date,
            template__isnull=False
        ).values(
            'template__name',
            'template__template_type'
        ).annotate(
            count=Count('id'),
            sent_count=Count('id', filter=Q(status='sent')),
            failed_count=Count('id', filter=Q(status='failed'))
        ).order_by('-count')
        
        return list(usage)

    @staticmethod
    def get_failed_messages(limit: int = 50) -> List[Dict]:
        """
        Get recent failed messages for retry.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of failed message details
        """
        failed_messages = Message.objects.filter(
            status='failed'
        ).select_related(
            'recipient_patient',
            'template'
        ).order_by('-created_at')[:limit]
        
        results = []
        for msg in failed_messages:
            # Get the error from logs
            error_log = MessageLog.objects.filter(
                message=msg,
                status='failed'
            ).order_by('-timestamp').first()
            
            results.append({
                'id': msg.id,
                'patient_id': msg.recipient_patient.id,
                'patient_name': f"{msg.recipient_patient.first_name} {msg.recipient_patient.last_name}",
                'message_type': msg.message_type,
                'template': msg.template.name if msg.template else None,
                'error': error_log.error_message if error_log else 'Unknown error',
                'created_at': msg.created_at,
                'retry_count': MessageLog.objects.filter(message=msg).count() - 1
            })
        
        return results

    @staticmethod
    def get_hourly_volume(days: int = 1) -> Dict:
        """
        Get message volume by hour for the past N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with hourly volume data
        """
        from django.db.models.functions import TruncHour
        
        start_date = timezone.now() - timedelta(days=days)
        
        hourly_data = Message.objects.filter(
            created_at__gte=start_date
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            count=Count('id'),
            sent=Count('id', filter=Q(status='sent')),
            failed=Count('id', filter=Q(status='failed'))
        ).order_by('hour')
        
        return {
            'hourly_data': list(hourly_data),
            'period_days': days
        }

    @staticmethod
    def get_patient_message_history(patient_id: int, limit: int = 20) -> List[Dict]:
        """
        Get message history for a specific patient.
        
        Args:
            patient_id: Patient ID
            limit: Maximum number of messages
            
        Returns:
            List of message history
        """
        messages = Message.objects.filter(
            recipient_patient_id=patient_id
        ).select_related('template').order_by('-created_at')[:limit]
        
        return [{
            'id': msg.id,
            'message_type': msg.message_type,
            'template': msg.template.name if msg.template else None,
            'status': msg.status,
            'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
            'created_at': msg.created_at,
            'sent_at': msg.sent_at,
        } for msg in messages]

    @staticmethod
    def get_dashboard_summary() -> Dict:
        """
        Get comprehensive dashboard summary.
        
        Returns:
            Dict with all key metrics
        """
        now = timezone.now()
        
        # Today's stats
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_messages = Message.objects.filter(created_at__gte=today_start)
        
        # This week's stats
        week_start = now - timedelta(days=7)
        week_messages = Message.objects.filter(created_at__gte=week_start)
        
        # This month's stats
        month_start = now - timedelta(days=30)
        month_messages = Message.objects.filter(created_at__gte=month_start)
        
        return {
            'today': {
                'total': today_messages.count(),
                'sent': today_messages.filter(status='sent').count(),
                'failed': today_messages.filter(status='failed').count(),
                'pending': today_messages.filter(status='pending').count(),
            },
            'this_week': {
                'total': week_messages.count(),
                'sent': week_messages.filter(status='sent').count(),
                'failed': week_messages.filter(status='failed').count(),
            },
            'this_month': {
                'total': month_messages.count(),
                'sent': month_messages.filter(status='sent').count(),
                'failed': month_messages.filter(status='failed').count(),
            },
            'overall': {
                'total_messages': Message.objects.count(),
                'total_patients': Message.objects.values('recipient_patient').distinct().count(),
                'active_templates': MessageTemplate.objects.filter(is_active=True).count(),
            }
        }
