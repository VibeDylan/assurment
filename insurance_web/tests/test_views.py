import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from insurance_web.models import Profile, Appointment, Prediction
from decimal import Decimal


@pytest.mark.django_db
class TestUserViews:
    
    def setup_method(self):
        self.client = Client()
    
    def test_home_view(self):
        response = self.client.get(reverse('insurance_web:home'))
        assert response.status_code == 200, "La page d'accueil devrait être accessible"
    
    def test_signup_view_get(self):
        response = self.client.get(reverse('insurance_web:signup'))
        assert response.status_code == 200, "Le formulaire d'inscription devrait être accessible"
        assert 'form' in response.context, "Le formulaire devrait être dans le contexte"
    
    def test_signup_view_post_valid(self):
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
        assert user.profile.role == 'user', "Le rôle par défaut devrait être 'user'"
        
        assert response.status_code == 302, "Il devrait y avoir une redirection après inscription"
        
        response = self.client.get(reverse('insurance_web:home'))
        assert response.context['user'].is_authenticated, \
            "L'utilisateur devrait être connecté après inscription"
    
    def test_signup_view_post_invalid(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',
            'password1': 'short',
            'password2': 'short'
        }
        response = self.client.post(reverse('insurance_web:signup'), form_data)
        
        assert response.status_code == 200, "La page devrait être rechargée avec des erreurs"
        assert 'form' in response.context, "Le formulaire devrait être dans le contexte"
        assert not response.context['form'].is_valid(), "Le formulaire devrait être invalide"
        
        assert not User.objects.filter(email='invalid-email').exists(), \
            "L'utilisateur ne devrait pas être créé avec des données invalides"
    
    def test_login_view(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post(reverse('insurance_web:login'), {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        
        assert response.status_code == 302, "Il devrait y avoir une redirection après connexion"
        
        response = self.client.get(reverse('insurance_web:home'))
        assert response.context['user'].is_authenticated, "L'utilisateur devrait être connecté"
        assert response.context['user'] == user, "Le bon utilisateur devrait être connecté"
    
    def test_logout_view(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')
        
        response = self.client.post(reverse('insurance_web:logout'))
        
        assert response.status_code == 302, "Il devrait y avoir une redirection après déconnexion"
        
        response = self.client.get(reverse('insurance_web:home'))
        assert not response.context['user'].is_authenticated, \
            "L'utilisateur devrait être déconnecté"
    
    def test_profile_view(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')
        
        Prediction.objects.create(
            user=user,
            created_by=user,
            predicted_amount=Decimal('1000.00')
        )
        
        response = self.client.get(reverse('insurance_web:profile'))
        assert response.status_code == 200, "Le profil devrait être accessible"


@pytest.mark.django_db
class TestConseillerViews:
    
    def setup_method(self):
        self.client = Client()
    
    def test_conseiller_dashboard_view(self):
        conseiller = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller.profile.role = 'conseiller'
        conseiller.profile.save()
        
        self.client.login(username='conseiller@example.com', password='testpass123')
        
        response = self.client.get(reverse('insurance_web:conseiller_dashboard'))
        assert response.status_code == 200, "Le dashboard conseiller devrait être accessible"
        
        normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='testpass123'
        )
        normal_user.profile.role = 'user'
        normal_user.profile.save()
        
        self.client.login(username='normal@example.com', password='testpass123')
        response = self.client.get(reverse('insurance_web:conseiller_dashboard'))
        assert response.status_code == 302, "Le user normal devrait être redirigé"


@pytest.mark.django_db
class TestAdminViews:
    
    def setup_method(self):
        self.client = Client()
    
    def test_admin_dashboard_view(self):
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin.profile.role = 'admin'
        admin.profile.save()
        
        self.client.login(username='admin@example.com', password='testpass123')
        
        response = self.client.get(reverse('insurance_web:admin_dashboard'))
        assert response.status_code == 200, "Le dashboard admin devrait être accessible"
        
        conseiller = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller.profile.role = 'conseiller'
        conseiller.profile.save()
        
        self.client.login(username='conseiller@example.com', password='testpass123')
        response = self.client.get(reverse('insurance_web:admin_dashboard'))
        assert response.status_code == 302, "Le conseiller devrait être redirigé"
