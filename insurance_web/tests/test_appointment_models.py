import pytest
from django.contrib.auth.models import User
from insurance_web.models import Appointment
from django.utils import timezone

@pytest.mark.django_db
class TestAppointmentModel:
    def test_appointment_creation(self):
        conseiller = User.objects.create_user(
            username='testconseiller',
            email='conseiller@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Conseiller'
        )
        client = User.objects.create_user(
            username='testclient',
            email='client@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Client'
        )
        appointment = Appointment.objects.create(
            conseiller=conseiller,
            client=client,
            date_time=timezone.now(),
            duration_minutes=60,
            notes='Test appointment'
        )
        assert appointment.conseiller == conseiller, "Le conseiller devrait être le bon"
        assert appointment.client == client, "Le client devrait être le bon"
        assert appointment.duration_minutes == 60, "La durée devrait être le bon"

    def test_appointment_str_method(self):
        conseiller = User.objects.create_user(
            username='testconseiller',
            email='conseiller@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Conseiller'
        )
        client = User.objects.create_user(
            username='testclient',
            email='client@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Client'
        )
        appointment = Appointment.objects.create(
            conseiller=conseiller,
            client=client,
            date_time=timezone.now(),
            duration_minutes=60,
            notes='Test appointment'
        )
        assert str(appointment) == f"Appointment {conseiller.get_full_name()} - {client.get_full_name()} - {appointment.date_time.strftime('%m/%d/%Y %H:%M')}", "Le __str__ devrait retourner le bon format"