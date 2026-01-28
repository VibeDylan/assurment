import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from insurance_web.models import Profile, Appointment, Prediction
from decimal import Decimal


@pytest.mark.django_db
class TestEndToEndWorkflows:
    
    def setup_method(self):
        self.client = Client()
    
    def test_user_registration_workflow(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post(reverse('insurance_web:signup'), form_data)
        
        assert User.objects.filter(email='john.doe@example.com').exists(), \
            "L'utilisateur devrait être créé"
        user = User.objects.get(email='john.doe@example.com')
        assert hasattr(user, 'profile'), "Le profil devrait être créé"
        
        assert response.status_code == 302, "Il devrait y avoir une redirection"
        
        response = self.client.get(reverse('insurance_web:profile'))
        assert response.status_code == 200, "Le profil devrait être accessible"
        assert response.context['user'].is_authenticated, \
            "L'utilisateur devrait être connecté automatiquement"
    
    def test_prediction_workflow(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('insurance_web:predict'))
        assert response.status_code == 200, "La page de prédiction devrait être accessible"
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        response = self.client.post(reverse('insurance_web:predict'), form_data)
        
        assert Prediction.objects.filter(user=user).exists(), \
            "La prédiction devrait être créée"
        
        
        response = self.client.get(reverse('insurance_web:profile'))
        assert response.status_code == 200, "Le profil devrait être accessible"
    
    def test_appointment_booking_workflow(self):
        conseiller = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller.profile.role = 'conseiller'
        conseiller.profile.save()
        
        client = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='testpass123'
        )
        self.client.login(username='client@example.com', password='testpass123')
        
        response = self.client.get(reverse('insurance_web:conseillers_list'))
        assert response.status_code == 200, "La liste des conseillers devrait être accessible"
        
        
        future_date = timezone.now() + timedelta(days=1)
        form_data = {
            'date_time': future_date.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
            'notes': 'Test appointment'
        }
        
        
    
    def test_conseiller_client_management_workflow(self):
        conseiller = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller.profile.role = 'conseiller'
        conseiller.profile.save()
        
        client = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='testpass123'
        )
        
        self.client.login(username='conseiller@example.com', password='testpass123')
        
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        
    
    def test_admin_user_management_workflow(self):
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin.profile.role = 'admin'
        admin.profile.save()
        
        self.client.login(username='admin@example.com', password='testpass123')
        
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'role': 'user'
        }
        
        
        
        
        
    
    def test_role_based_access_workflow(self):
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        user.profile.role = 'user'
        user.profile.save()
        
        conseiller = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller.profile.role = 'conseiller'
        conseiller.profile.save()
        
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin.profile.role = 'admin'
        admin.profile.save()
        
        self.client.login(username='user@example.com', password='testpass123')
        response = self.client.get(reverse('insurance_web:home'))
        assert response.status_code == 200, "Le user devrait accéder à la page d'accueil"
        
        self.client.login(username='conseiller@example.com', password='testpass123')
        response = self.client.get(reverse('insurance_web:conseiller_dashboard'))
        assert response.status_code == 200, "Le conseiller devrait accéder au dashboard conseiller"
        
        self.client.login(username='admin@example.com', password='testpass123')
        response = self.client.get(reverse('insurance_web:admin_dashboard'))
        assert response.status_code == 200, "L'admin devrait accéder au dashboard admin"
        response = self.client.get(reverse('insurance_web:conseiller_dashboard'))
        assert response.status_code == 200, "L'admin devrait aussi accéder au dashboard conseiller"
