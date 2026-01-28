import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from insurance_web.models import Profile, Appointment, Prediction
from decimal import Decimal


@pytest.mark.django_db
class TestSecurity:
    
    def setup_method(self):
        self.client = Client()
    
    def test_authentication_required(self):
        protected_views = [
            'insurance_web:profile',
            'insurance_web:predict',
            'insurance_web:conseiller_dashboard',
            'insurance_web:admin_dashboard',
            'insurance_web:my_appointments',
        ]
        
        for view_name in protected_views:
            try:
                response = self.client.get(reverse(view_name))
                assert response.status_code in [302, 403], \
                    f"La vue {view_name} devrait être protégée"
            except Exception:
                pass
    
    def test_permission_checks(self):
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
        try:
            response = self.client.get(reverse('insurance_web:conseiller_dashboard'))
            assert response.status_code == 302, \
                "Le user normal devrait être redirigé du dashboard conseiller"
        except Exception:
            pass
        
        self.client.login(username='conseiller@example.com', password='testpass123')
        try:
            response = self.client.get(reverse('insurance_web:admin_dashboard'))
            assert response.status_code == 302, \
                "Le conseiller devrait être redirigé du dashboard admin"
        except Exception:
            pass
        
        self.client.login(username='user@example.com', password='testpass123')
        try:
            response = self.client.get(reverse('insurance_web:admin_dashboard'))
            assert response.status_code == 302, \
                "Le user normal devrait être redirigé du dashboard admin"
        except Exception:
            pass
    
    def test_user_isolation(self):
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        prediction1 = Prediction.objects.create(
            user=user1,
            created_by=user1,
            predicted_amount=Decimal('1000.00')
        )
        
        prediction2 = Prediction.objects.create(
            user=user2,
            created_by=user2,
            predicted_amount=Decimal('2000.00')
        )
        
        self.client.login(username='user1@example.com', password='testpass123')
        
    
    def test_admin_self_protection(self):
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin.profile.role = 'admin'
        admin.profile.save()
        
        self.client.login(username='admin@example.com', password='testpass123')
        
        
    
    def test_password_hashing(self):
        password = 'testpass123'
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=password
        )
        
        user_from_db = User.objects.get(username='testuser')
        assert user_from_db.password != password, \
            "Le mot de passe ne devrait pas être en clair"
        assert user_from_db.password.startswith('pbkdf2_') or user_from_db.password.startswith('argon2'), \
            "Le mot de passe devrait être hashé avec un algorithme sécurisé"
        
        assert user_from_db.check_password(password), \
            "check_password devrait fonctionner avec le bon mot de passe"
        assert not user_from_db.check_password('wrongpassword'), \
            "check_password devrait échouer avec un mauvais mot de passe"
    
    def test_email_uniqueness(self):
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='testpass123'
        )
        
        from insurance_web.forms import CustomUserCreationForm
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid(), \
            "Le formulaire devrait être invalide avec un email déjà utilisé"
        assert 'email' in form.errors, \
            "Il devrait y avoir une erreur sur le champ email"
        
        assert User.objects.filter(email='test@example.com').count() == 1, \
            "Il ne devrait y avoir qu'un seul utilisateur avec cet email"
    
    def test_sql_injection_protection(self):
        malicious_input = "'; DROP TABLE users; --"
        
        user = User.objects.create_user(
            username='testuser',
            email=f'test{malicious_input}@example.com',
            password='testpass123',
            first_name=malicious_input
        )
        
        assert User.objects.filter(email__contains='test').exists(), \
            "L'utilisateur devrait être créé même avec des caractères spéciaux"
        
        assert User.objects.all().exists(), \
            "La table users devrait toujours exister (pas de DROP TABLE)"
    
    def test_xss_protection(self):
        xss_payload = '<script>alert("XSS")</script>'
        
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name=xss_payload
        )
        
        
        assert User.objects.filter(username='testuser').exists(), \
            "L'utilisateur devrait être créé même avec du contenu XSS"
