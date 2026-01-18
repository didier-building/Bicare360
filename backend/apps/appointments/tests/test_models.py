"""
Tests for appointment models.
Following TDD: Write tests first, then implement models.
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, time
from apps.appointments.models import Appointment, AppointmentReminder
from apps.patients.models import Patient
from apps.enrollment.models import Hospital


@pytest.mark.django_db
class TestAppointmentModel:
    """Test Appointment model."""
    
    def test_create_appointment_with_required_fields(self):
        """Test creating appointment with only required fields."""
        patient = Patient.objects.create(
            first_name="Jean",
            last_name="Mugabo",
            national_id="1199012345678901",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987654"
        )
        hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TH001",
            hospital_type="district",
            phone_number="+250788123456",
            province="Kigali",
            district="Gasabo"
        )
        
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="follow_up",
            status="scheduled"
        )
        
        assert appointment.patient == patient
        assert appointment.hospital == hospital
        assert appointment.appointment_type == "follow_up"
        assert appointment.status == "scheduled"
        assert appointment.created_at is not None
        
    def test_appointment_type_choices(self):
        """Test appointment type choices are valid."""
        patient = Patient.objects.create(
            first_name="Test",
            last_name="User",
            national_id="1199012345678902",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987655"
        )
        hospital = Hospital.objects.create(
            name="Hospital",
            code="H001",
            hospital_type="district",
            phone_number="+250788123457",
            province="Kigali",
            district="Gasabo"
        )
        
        valid_types = ['follow_up', 'medication_review', 'consultation', 'emergency', 'routine_checkup']
        
        for apt_type in valid_types:
            appointment = Appointment.objects.create(
                patient=patient,
                hospital=hospital,
                appointment_datetime=timezone.now() + timedelta(days=1),
                appointment_type=apt_type,
                status="scheduled"
            )
            assert appointment.appointment_type == apt_type
            
    def test_appointment_status_choices(self):
        """Test appointment status choices."""
        patient = Patient.objects.create(
            first_name="Status",
            last_name="Test",
            national_id="1199012345678903",
            date_of_birth="1990-01-01",
            gender="F",
            phone_number="+250788987656"
        )
        hospital = Hospital.objects.create(
            name="Status Hospital",
            code="SH001",
            hospital_type="district",
            phone_number="+250788123458",
            province="Kigali",
            district="Gasabo"
        )
        
        valid_statuses = ['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show', 'rescheduled']
        
        for status in valid_statuses:
            appointment = Appointment.objects.create(
                patient=patient,
                hospital=hospital,
                appointment_datetime=timezone.now() + timedelta(days=1),
                appointment_type="consultation",
                status=status
            )
            assert appointment.status == status
            
    def test_appointment_location_type_choices(self):
        """Test location type choices."""
        patient = Patient.objects.create(
            first_name="Location",
            last_name="Test",
            national_id="1199012345678904",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987657"
        )
        hospital = Hospital.objects.create(
            name="Location Hospital",
            code="LH001",
            hospital_type="district",
            phone_number="+250788123459",
            province="Kigali",
            district="Gasabo"
        )
        
        location_types = ['hospital', 'home_visit', 'telemedicine']
        
        for location in location_types:
            appointment = Appointment.objects.create(
                patient=patient,
                hospital=hospital,
                appointment_datetime=timezone.now() + timedelta(days=1),
                appointment_type="consultation",
                status="scheduled",
                location_type=location
            )
            assert appointment.location_type == location
            
    def test_appointment_str_representation(self):
        """Test string representation."""
        patient = Patient.objects.create(
            first_name="Jean",
            last_name="Mugabo",
            national_id="1199012345678905",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987658"
        )
        hospital = Hospital.objects.create(
            name="Test Hospital",
            code="TH002",
            hospital_type="district",
            phone_number="+250788123460",
            province="Kigali",
            district="Gasabo"
        )
        
        apt_datetime = timezone.now() + timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=apt_datetime,
            appointment_type="follow_up",
            status="scheduled"
        )
        
        expected = f"{patient.full_name} - follow_up on {apt_datetime.strftime('%Y-%m-%d %H:%M')}"
        assert str(appointment) == expected
        
    def test_appointment_ordering(self):
        """Test appointments are ordered by datetime."""
        patient = Patient.objects.create(
            first_name="Order",
            last_name="Test",
            national_id="1199012345678906",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987659"
        )
        hospital = Hospital.objects.create(
            name="Order Hospital",
            code="OH001",
            hospital_type="district",
            phone_number="+250788123461",
            province="Kigali",
            district="Gasabo"
        )
        
        apt1 = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=3),
            appointment_type="consultation",
            status="scheduled"
        )
        apt2 = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="follow_up",
            status="scheduled"
        )
        apt3 = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=2),
            appointment_type="medication_review",
            status="scheduled"
        )
        
        appointments = list(Appointment.objects.all())
        assert appointments[0] == apt2  # Earliest first
        assert appointments[1] == apt3
        assert appointments[2] == apt1
        
    def test_appointment_is_upcoming_property(self):
        """Test is_upcoming computed property."""
        patient = Patient.objects.create(
            first_name="Upcoming",
            last_name="Test",
            national_id="1199012345678907",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987660"
        )
        hospital = Hospital.objects.create(
            name="Upcoming Hospital",
            code="UH001",
            hospital_type="district",
            phone_number="+250788123462",
            province="Kigali",
            district="Gasabo"
        )
        
        # Future appointment
        future_apt = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        assert future_apt.is_upcoming is True
        
        # Past appointment
        past_apt = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() - timedelta(days=1),
            appointment_type="consultation",
            status="completed"
        )
        assert past_apt.is_upcoming is False
        
    def test_appointment_is_overdue_property(self):
        """Test is_overdue computed property."""
        patient = Patient.objects.create(
            first_name="Overdue",
            last_name="Test",
            national_id="1199012345678908",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987661"
        )
        hospital = Hospital.objects.create(
            name="Overdue Hospital",
            code="ODH001",
            hospital_type="district",
            phone_number="+250788123463",
            province="Kigali",
            district="Gasabo"
        )
        
        # Past scheduled appointment (overdue)
        overdue_apt = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() - timedelta(hours=1),
            appointment_type="consultation",
            status="scheduled"
        )
        assert overdue_apt.is_overdue is True
        
        # Future appointment (not overdue)
        future_apt = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        assert future_apt.is_overdue is False
        
        # Completed appointment (not overdue even if past)
        completed_apt = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() - timedelta(days=1),
            appointment_type="consultation",
            status="completed"
        )
        assert completed_apt.is_overdue is False
        
    def test_appointment_cascade_delete_patient(self):
        """Test appointment is deleted when patient is deleted."""
        patient = Patient.objects.create(
            first_name="Cascade",
            last_name="Test",
            national_id="1199012345678909",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987662"
        )
        hospital = Hospital.objects.create(
            name="Cascade Hospital",
            code="CH001",
            hospital_type="district",
            phone_number="+250788123464",
            province="Kigali",
            district="Gasabo"
        )
        
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        appointment_id = appointment.id
        patient.delete()
        
        assert not Appointment.objects.filter(id=appointment_id).exists()
        
    def test_appointment_protect_hospital(self):
        """Test appointment prevents hospital deletion."""
        patient = Patient.objects.create(
            first_name="Protect",
            last_name="Test",
            national_id="1199012345678910",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987663"
        )
        hospital = Hospital.objects.create(
            name="Protect Hospital",
            code="PH001",
            hospital_type="district",
            phone_number="+250788123465",
            province="Kigali",
            district="Gasabo"
        )
        
        Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        with pytest.raises(Exception):  # ProtectedError
            hospital.delete()
            
    def test_appointment_with_optional_fields(self):
        """Test appointment with all optional fields."""
        patient = Patient.objects.create(
            first_name="Optional",
            last_name="Test",
            national_id="1199012345678911",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987664"
        )
        hospital = Hospital.objects.create(
            name="Optional Hospital",
            code="OPH001",
            hospital_type="district",
            phone_number="+250788123466",
            province="Kigali",
            district="Gasabo"
        )
        
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled",
            location_type="telemedicine",
            provider_name="Dr. Mutesi",
            reason="Follow-up consultation",
            notes="Patient requested video call",
            notes_kinyarwanda="Umukiriya yasabye guhamagara kuri video",
            duration_minutes=30
        )
        
        assert appointment.provider_name == "Dr. Mutesi"
        assert appointment.reason == "Follow-up consultation"
        assert appointment.notes == "Patient requested video call"
        assert appointment.notes_kinyarwanda == "Umukiriya yasabye guhamagara kuri video"
        assert appointment.duration_minutes == 30
        
    def test_filter_appointments_by_status(self):
        """Test filtering appointments by status."""
        patient = Patient.objects.create(
            first_name="Filter",
            last_name="Test",
            national_id="1199012345678912",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987665"
        )
        hospital = Hospital.objects.create(
            name="Filter Hospital",
            code="FH001",
            hospital_type="district",
            phone_number="+250788123467",
            province="Kigali",
            district="Gasabo"
        )
        
        scheduled = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        confirmed = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=2),
            appointment_type="follow_up",
            status="confirmed"
        )
        
        scheduled_apts = Appointment.objects.filter(status="scheduled")
        assert scheduled in scheduled_apts
        assert confirmed not in scheduled_apts
        
    def test_filter_appointments_by_patient(self):
        """Test filtering appointments by patient."""
        patient1 = Patient.objects.create(
            first_name="Patient",
            last_name="One",
            national_id="1199012345678913",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987666"
        )
        patient2 = Patient.objects.create(
            first_name="Patient",
            last_name="Two",
            national_id="1199012345678914",
            date_of_birth="1990-01-01",
            gender="F",
            phone_number="+250788987667"
        )
        hospital = Hospital.objects.create(
            name="Filter Hospital",
            code="FH002",
            hospital_type="district",
            phone_number="+250788123468",
            province="Kigali",
            district="Gasabo"
        )
        
        apt1 = Appointment.objects.create(
            patient=patient1,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        apt2 = Appointment.objects.create(
            patient=patient2,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        patient1_apts = Appointment.objects.filter(patient=patient1)
        assert apt1 in patient1_apts
        assert apt2 not in patient1_apts
        
    def test_appointment_timestamps(self):
        """Test created_at and updated_at timestamps."""
        patient = Patient.objects.create(
            first_name="Timestamp",
            last_name="Test",
            national_id="1199012345678915",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987668"
        )
        hospital = Hospital.objects.create(
            name="Timestamp Hospital",
            code="TSH001",
            hospital_type="district",
            phone_number="+250788123469",
            province="Kigali",
            district="Gasabo"
        )
        
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        assert appointment.created_at is not None
        assert appointment.updated_at is not None
        assert appointment.updated_at >= appointment.created_at


@pytest.mark.django_db
class TestAppointmentReminderModel:
    """Test AppointmentReminder model."""
    
    def test_create_reminder_with_required_fields(self):
        """Test creating reminder with required fields."""
        patient = Patient.objects.create(
            first_name="Reminder",
            last_name="Test",
            national_id="1199012345678916",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987669"
        )
        hospital = Hospital.objects.create(
            name="Reminder Hospital",
            code="RH001",
            hospital_type="district",
            phone_number="+250788123470",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        
        assert reminder.appointment == appointment
        assert reminder.reminder_type == "sms"
        assert reminder.status == "pending"
        
    def test_reminder_type_choices(self):
        """Test reminder type choices."""
        patient = Patient.objects.create(
            first_name="Type",
            last_name="Test",
            national_id="1199012345678917",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987670"
        )
        hospital = Hospital.objects.create(
            name="Type Hospital",
            code="TYH001",
            hospital_type="district",
            phone_number="+250788123471",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        types = ['sms', 'whatsapp', 'email', 'call']
        
        for reminder_type in types:
            reminder = AppointmentReminder.objects.create(
                appointment=appointment,
                reminder_datetime=timezone.now() + timedelta(hours=1),
                reminder_type=reminder_type,
                status="pending"
            )
            assert reminder.reminder_type == reminder_type
            
    def test_reminder_status_choices(self):
        """Test reminder status choices."""
        patient = Patient.objects.create(
            first_name="Status",
            last_name="Reminder",
            national_id="1199012345678918",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987671"
        )
        hospital = Hospital.objects.create(
            name="Status Hospital",
            code="STH001",
            hospital_type="district",
            phone_number="+250788123472",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        statuses = ['pending', 'sent', 'failed', 'cancelled']
        
        for status in statuses:
            reminder = AppointmentReminder.objects.create(
                appointment=appointment,
                reminder_datetime=timezone.now() + timedelta(hours=1),
                reminder_type="sms",
                status=status
            )
            assert reminder.status == status
            
    def test_reminder_str_representation(self):
        """Test string representation."""
        patient = Patient.objects.create(
            first_name="Jean",
            last_name="Mugabo",
            national_id="1199012345678919",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987672"
        )
        hospital = Hospital.objects.create(
            name="String Hospital",
            code="STRH001",
            hospital_type="district",
            phone_number="+250788123473",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        
        expected = f"SMS reminder for {appointment} - pending"
        assert str(reminder) == expected
        
    def test_reminder_ordering(self):
        """Test reminders are ordered by datetime."""
        patient = Patient.objects.create(
            first_name="Order",
            last_name="Reminder",
            national_id="1199012345678920",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987673"
        )
        hospital = Hospital.objects.create(
            name="Order Hospital",
            code="ORH001",
            hospital_type="district",
            phone_number="+250788123474",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        reminder1 = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        reminder2 = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=2),
            reminder_type="whatsapp",
            status="pending"
        )
        reminder3 = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=12),
            reminder_type="email",
            status="pending"
        )
        
        reminders = list(AppointmentReminder.objects.all())
        assert reminders[0] == reminder2  # Earliest first
        assert reminders[1] == reminder3
        assert reminders[2] == reminder1
        
    def test_reminder_cascade_delete_appointment(self):
        """Test reminder is deleted when appointment is deleted."""
        patient = Patient.objects.create(
            first_name="Delete",
            last_name="Test",
            national_id="1199012345678921",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987674"
        )
        hospital = Hospital.objects.create(
            name="Delete Hospital",
            code="DH001",
            hospital_type="district",
            phone_number="+250788123475",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        
        reminder_id = reminder.id
        appointment.delete()
        
        assert not AppointmentReminder.objects.filter(id=reminder_id).exists()
        
    def test_reminder_is_due_property(self):
        """Test is_due computed property."""
        patient = Patient.objects.create(
            first_name="Due",
            last_name="Test",
            national_id="1199012345678922",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987675"
        )
        hospital = Hospital.objects.create(
            name="Due Hospital",
            code="DUH001",
            hospital_type="district",
            phone_number="+250788123476",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        # Past reminder that's pending (due)
        due_reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() - timedelta(minutes=5),
            reminder_type="sms",
            status="pending"
        )
        assert due_reminder.is_due is True
        
        # Future reminder (not due)
        future_reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=1),
            reminder_type="sms",
            status="pending"
        )
        assert future_reminder.is_due is False
        
        # Past reminder that was sent (not due anymore)
        sent_reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() - timedelta(hours=1),
            reminder_type="sms",
            status="sent"
        )
        assert sent_reminder.is_due is False
        
    def test_reminder_timestamps(self):
        """Test created_at and sent_at timestamps."""
        patient = Patient.objects.create(
            first_name="Timestamp",
            last_name="Reminder",
            national_id="1199012345678923",
            date_of_birth="1990-01-01",
            gender="M",
            phone_number="+250788987676"
        )
        hospital = Hospital.objects.create(
            name="Timestamp Hospital",
            code="TSRH001",
            hospital_type="district",
            phone_number="+250788123477",
            province="Kigali",
            district="Gasabo"
        )
        appointment = Appointment.objects.create(
            patient=patient,
            hospital=hospital,
            appointment_datetime=timezone.now() + timedelta(days=1),
            appointment_type="consultation",
            status="scheduled"
        )
        
        reminder = AppointmentReminder.objects.create(
            appointment=appointment,
            reminder_datetime=timezone.now() + timedelta(hours=23),
            reminder_type="sms",
            status="pending"
        )
        
        assert reminder.created_at is not None
        assert reminder.sent_at is None
        
        # Simulate sending
        reminder.status = "sent"
        reminder.sent_at = timezone.now()
        reminder.save()
        
        assert reminder.sent_at is not None
