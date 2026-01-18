# Phase 2 Planning Guide: Digital Patient Engagement

**Timeline:** Weeks 3-4  
**Status:** ⏸️ BLOCKED ON API CREDENTIALS  
**Priority:** CRITICAL  

---

## 📋 Phase 2 Overview

### Objective
Implement SMS and WhatsApp messaging capabilities to enable direct patient communication for:
- Appointment reminders
- Medication adherence reminders
- Discharge follow-up messages
- Two-way communication (optional)

### Dependencies
1. **CRITICAL:** Africa's Talking API account & credentials
2. **BLOCKING:** WhatsApp Business API template approval (24-48 hours)
3. **OPTIONAL:** Hospital SMS gateway integration

---

## 🔑 API Credentials Required

### Africa's Talking Setup

**Account Requirements:**
```
1. Create account at: https://africastalking.com
2. Activate API access (may require verification)
3. Get API Key and username
4. Configure SMS sender ID (e.g., "BiCare360" - 11 chars max)
5. Request WhatsApp Business Account setup
```

**Configuration Location:**
```python
# backend/bicare360/settings/base.py
AFRICASTALKING_USERNAME = env("AFRICASTALKING_USERNAME")
AFRICASTALKING_API_KEY = env("AFRICASTALKING_API_KEY")
AFRICASTALKING_FROM = env("AFRICASTALKING_FROM", default="BiCare360")
AFRICASTALKING_SANDBOX = env.bool("AFRICASTALKING_SANDBOX", default=True)
```

**Environment Setup (.env):**
```bash
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key
AFRICASTALKING_FROM=BiCare360
AFRICASTALKING_SANDBOX=True  # Set to False for production
```

---

## 🏗️ Implementation Architecture

### Current Infrastructure (Week 2 Complete)

Already implemented and ready to use:

**Database Models:**
```
MessageTemplate - Template definitions with variables
├─ template_type: choice (SMS, WhatsApp, Email)
├─ message_type: choice (appointment, medication, discharge, etc.)
├─ content_english, content_kinyarwanda
├─ is_active: boolean

Message - Individual message instances
├─ recipient_patient: FK
├─ template: FK
├─ status: choice (pending, queued, sent, failed)
├─ recipient_phone: cached value
├─ content_rendered: filled template
├─ appointment: optional FK

MessageLog - Audit trail
├─ message: FK
├─ status: choice
├─ timestamp
├─ error_details: nullable

MessageQueue - Priority queue for sending
├─ status: choice (pending, processing, sent, failed)
├─ priority: int (1-4, where 1=highest)
├─ message_type: choice
├─ scheduled_time: datetime
├─ retry_count: int (max 5)
├─ appointment: FK
```

**Celery Tasks (Ready for integration):**
```python
apps/messaging/tasks.py:
├─ send_message_task(message_id) - Send single message
├─ send_bulk_messages(recipients, content) - Bulk sending
├─ schedule_appointment_reminders() - Cron job
├─ process_message_queue() - Background processor
```

**API Endpoints (Ready for use):**
```
GET/POST /api/v1/message-templates/
GET/POST /api/v1/messages/
POST /api/v1/messages/{id}/send/
POST /api/v1/messages/send-bulk/
GET /api/v1/message-logs/
GET/POST /api/v1/message-queue/
```

---

## 📱 Implementation Roadmap

### Phase 2A: SMS Integration (Weeks 3-3.5)

#### Step 1: Install Africa's Talking SDK
```bash
pip install africastalking
requirements/base.txt: +africastalking
```

#### Step 2: Create SMS Service Layer
```python
# apps/messaging/services.py

class AfricasTalkingService:
    """Handle Africa's Talking API integration"""
    
    def __init__(self):
        self.client = africastalking.SMS(
            username=settings.AFRICASTALKING_USERNAME,
            api_key=settings.AFRICASTALKING_API_KEY
        )
    
    def send_sms(self, phone: str, message: str) -> dict:
        """Send SMS and return status"""
        response = self.client.send(message, [phone])
        return response
    
    def send_bulk_sms(self, recipients: List[str], message: str) -> dict:
        """Send bulk SMS"""
        response = self.client.send(message, recipients)
        return response
    
    def get_balance(self) -> float:
        """Check account balance"""
        return self.client.get_balance()
```

#### Step 3: Update Message Model Service
```python
# apps/messaging/services.py - add to existing

class MessageService:
    """High-level message sending service"""
    
    def send_message(self, message_id: int) -> bool:
        """Send message via appropriate channel"""
        message = Message.objects.get(id=message_id)
        
        if message.message_type == 'sms':
            return self._send_sms(message)
        elif message.message_type == 'whatsapp':
            return self._send_whatsapp(message)
        elif message.message_type == 'email':
            return self._send_email(message)
    
    def _send_sms(self, message: Message) -> bool:
        service = AfricasTalkingService()
        try:
            response = service.send_sms(
                message.recipient_phone,
                message.content_rendered
            )
            # Log response
            MessageLog.objects.create(
                message=message,
                status='sent',
                response_data=response
            )
            message.status = 'sent'
            message.save()
            return True
        except Exception as e:
            MessageLog.objects.create(
                message=message,
                status='failed',
                error_details=str(e)
            )
            return False
```

#### Step 4: Update Celery Tasks
```python
# apps/messaging/tasks.py

from celery import shared_task
from .services import MessageService

@shared_task
def send_message_task(message_id):
    """Send message asynchronously"""
    service = MessageService()
    return service.send_message(message_id)

@shared_task
def schedule_appointment_reminders():
    """Send reminders for upcoming appointments"""
    from datetime import timedelta
    from django.utils import timezone
    
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming = Appointment.objects.filter(
        appointment_datetime__date=tomorrow.date(),
        status='confirmed'
    )
    
    for appointment in upcoming:
        # Create message
        template = MessageTemplate.objects.get(
            message_type='appointment_reminder'
        )
        message = Message.objects.create(
            recipient_patient=appointment.patient,
            template=template,
            appointment=appointment,
            message_type='sms',
            content_rendered=template.content_kinyarwanda.format(
                patient_name=appointment.patient.first_name,
                appointment_time=appointment.appointment_datetime.strftime('%H:%M')
            )
        )
        
        # Send immediately or queue
        send_message_task.delay(message.id)
```

### Phase 2B: WhatsApp Integration (Weeks 3.5-4)

#### Step 1: Request WhatsApp Template Approval
```
Africa's Talking WhatsApp Business Account Setup:

Templates needed:
1. appointment_reminder
   Variables: {patient_name}, {appointment_time}, {hospital_name}
   
2. medication_reminder
   Variables: {patient_name}, {medication_name}, {time}
   
3. discharge_followup
   Variables: {patient_name}, {follow_up_date}
   
4. test_reminder
   Variables: {patient_name}, {test_name}
```

#### Step 2: Update Service for WhatsApp
```python
# apps/messaging/services.py

class AfricasTalkingService:
    
    def __init__(self):
        self.sms_client = africastalking.SMS(...)
        self.whatsapp_client = africastalking.WhatsApp(
            api_key=settings.AFRICASTALKING_API_KEY
        )
    
    def send_whatsapp(self, phone: str, template_id: str, 
                      variables: dict) -> dict:
        """Send WhatsApp template message"""
        response = self.whatsapp_client.send_template(
            phone=phone,
            template_id=template_id,
            parameters=variables
        )
        return response
```

#### Step 3: Update Message Model for Templates
```python
# apps/messaging/models.py - extend Message

class Message(models.Model):
    # ... existing fields ...
    
    # For WhatsApp template messages
    template_id = models.CharField(max_length=100, null=True, blank=True)
    template_variables = models.JSONField(default=dict, blank=True)
```

### Phase 2C: Appointment Reminders (Weeks 3.5-4)

#### Implementation Steps:

**1. Create Reminder View:**
```python
# apps/appointments/views.py - add to AppointmentViewSet

@action(detail=True, methods=['post'])
def send_reminder(self, request, pk=None):
    """Manually send reminder for appointment"""
    appointment = self.get_object()
    
    from apps.messaging.tasks import send_message_task
    from apps.messaging.models import Message, MessageTemplate
    
    template = MessageTemplate.objects.get(
        message_type='appointment_reminder'
    )
    
    message = Message.objects.create(
        recipient_patient=appointment.patient,
        template=template,
        appointment=appointment,
        message_type='sms',
        content_rendered=template.render(patient=appointment.patient)
    )
    
    send_message_task.delay(message.id)
    return Response({'status': 'Reminder sent'})
```

**2. Setup Scheduled Task:**
```python
# bicare360/celery.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-appointment-reminders': {
        'task': 'apps.messaging.tasks.schedule_appointment_reminders',
        'schedule': crontab(hour=7, minute=0),  # 7 AM daily
    },
}
```

**3. Create Management Command:**
```bash
python manage.py send_appointment_reminders --days=1
```

---

## 📊 Testing Strategy

### Unit Tests
```python
# apps/messaging/tests/test_services.py

def test_send_sms():
    """Test SMS sending"""
    service = AfricasTalkingService()
    result = service.send_sms("+250788987654", "Test message")
    assert result['status'] == 'sent'

def test_send_whatsapp():
    """Test WhatsApp sending"""
    service = AfricasTalkingService()
    result = service.send_whatsapp(
        "+250788987654",
        "appointment_reminder",
        {"patient_name": "John", "time": "14:00"}
    )
    assert result['status'] == 'sent'
```

### Integration Tests
```python
def test_appointment_reminder_workflow():
    """Test full appointment reminder flow"""
    appointment = create_test_appointment()
    send_appointment_reminders()
    
    messages = Message.objects.filter(appointment=appointment)
    assert messages.exists()
    assert messages[0].status == 'sent'
```

### Sandbox Testing
```python
# Use Africa's Talking sandbox mode
AFRICASTALKING_SANDBOX = True

# Test numbers available in sandbox
TEST_PHONE = "+254718769881"
```

---

## 💰 Cost Estimation

### Africa's Talking Pricing (Approximate)

| Service | Cost | Volume |
|---------|------|--------|
| SMS (per message) | KES 0.80 (~$0.006) | Variable |
| WhatsApp (per message) | ~KES 2-5 | Premium |
| Monthly minimum | ~$20-50 | N/A |

### Estimated Monthly Costs (100 patients)

```
SMS appointment reminders: 400 messages × $0.006 = $2.40
Medication reminders: 2,000 messages × $0.006 = $12.00
Discharge follow-ups: 100 messages × $0.006 = $0.60
WhatsApp messages: 300 × $0.03 = $9.00
───────────────────────────────────────────────────
Estimated monthly: $24-50 (depends on volume)
```

---

## 🚀 Deployment Checklist

- [ ] Africa's Talking account created
- [ ] API key obtained and stored in .env
- [ ] SMS sender ID approved (BiCare360)
- [ ] WhatsApp Business Account created
- [ ] WhatsApp templates submitted for approval
- [ ] SDK installed: `pip install africastalking`
- [ ] Services implemented and tested
- [ ] Celery configured and running
- [ ] Appointment reminders scheduled
- [ ] Monitoring/alerts set up
- [ ] Backup SMS gateway configured (optional)

---

## 🔍 Monitoring & Alerts

### Metrics to Track
```python
# apps/messaging/admin.py

class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient_phone', 'status', 'message_type', 'sent_at']
    list_filter = ['status', 'message_type', 'created_at']
    search_fields = ['recipient_phone', 'content_rendered']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['recipient_phone', 'content_rendered', 'sent_at']
        return []
```

### Alert Conditions
```
- SMS send failure rate > 5%
- WhatsApp send failure rate > 10%
- Queue processing delay > 5 minutes
- Account balance < $10
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue: "Authentication failed" from Africa's Talking**
```
Solution:
1. Verify API key in .env
2. Check username in settings
3. Ensure account is active at africastalking.com
4. Test with sandbox mode first
```

**Issue: SMS not being sent**
```
Solution:
1. Check phone number format (+250...)
2. Verify message content is not empty
3. Check MessageQueue status
4. Review MessageLog for errors
5. Verify account has balance
```

**Issue: WhatsApp templates not approved**
```
Solution:
1. Ensure templates follow guidelines
2. Wait 24-48 hours for approval
3. Check rejection reason in AT dashboard
4. Resubmit with corrected content
5. Contact Africa's Talking support
```

---

## 📝 Next Actions (When API Credentials Available)

1. **Today:** Acquire Africa's Talking credentials
2. **Day 1:** Install SDK and configure environment
3. **Day 2-3:** Implement SMS service layer
4. **Day 3:** Test SMS sending in sandbox mode
5. **Day 4:** Submit WhatsApp templates
6. **Day 5:** Implement WhatsApp service (if approved)
7. **Day 6:** Setup appointment reminders
8. **Day 7:** Integration testing and deployment

---

## 📚 References

- Africa's Talking Docs: https://africastalking.com/sms/api
- WhatsApp Business API: https://africastalking.com/whatsapp
- Celery Beat Documentation: https://docs.celeryproject.io/en/stable/userguide/periodic-tasks.html
- Django REST Framework: https://www.django-rest-framework.org/

---

**Status:** Ready to implement upon credential acquisition  
**Estimated Duration:** 4-5 days (Weeks 3-4)  
**Success Criteria:** Appointment reminders delivered via SMS to test patients
