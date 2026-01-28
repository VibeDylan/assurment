from typing import Any


import pytest
from django.contrib.auth.models import User
from insurance_web.models import Appointment
from django.utils import timezone
from datetime import timedelta
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

    def test_appointment_ordering(self):
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
        appointment1 = Appointment.objects.create(
            conseiller=conseiller,
            client=client,
            date_time=timezone.now(),
            duration_minutes=60,
            notes='Test appointment 1'
        )
        appointment2 = Appointment.objects.create(
            conseiller=conseiller,
            client=client,
            date_time=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            notes='Test appointment 2'
        )
        assert list[Any](Appointment.objects.all()) == [appointment1, appointment2], "Les rendez-vous devraient être triés par date et heure"

    def test_appointment_cascade_deletion(self):
        conseiller = User.objects.create_user(
            username='testconseiller',
            email='conseiller@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Conseiller'
        )
        client1 = User.objects.create_user(
            username='testclient1',
            email='client1@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Client1'
        )
        client2 = User.objects.create_user(
            username='testclient2',
            email='client2@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Client2'
        )
        
        appointment1 = Appointment.objects.create(
            conseiller=conseiller,
            client=client1,
            date_time=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            notes='Test appointment 1'
        )
        appointment2 = Appointment.objects.create(
            conseiller=conseiller,
            client=client2,
            date_time=timezone.now(),
            duration_minutes=60,
            notes='Test appointment 2'
        )
        
        client1_id = client1.id
        client2_id = client2.id
        conseiller_id = conseiller.id
        
        client1.delete()
        assert not Appointment.objects.filter(client_id=client1_id).exists(), \
            "Les rendez-vous du client1 devraient être supprimés en cascade"
        assert Appointment.objects.filter(client_id=client2_id).exists(), \
            "Les rendez-vous du client2 devraient être conservés"
        
        conseiller.delete()
        assert not Appointment.objects.filter(conseiller_id=conseiller_id).exists(), \
            "Tous les rendez-vous du conseiller devraient être supprimés en cascade"
        assert not Appointment.objects.filter(client_id=client2_id).exists(), \
            "Le rendez-vous de client2 devrait aussi être supprimé car le conseiller a été supprimé"


    def test_appointment_date_time_validation(self):
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
        expected_date_time = timezone.now()
        appointment = Appointment.objects.create(
            conseiller=conseiller,
            client=client,
            date_time=expected_date_time,
            duration_minutes=60,
            notes='Test appointment'
        )
        assert appointment.date_time == expected_date_time, "La date et l'heure devrait être le bon"