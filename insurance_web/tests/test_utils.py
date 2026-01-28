import pytest
from django.contrib.auth.models import User, AnonymousUser
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from insurance_web.utils.decorators import (
    conseiller_required,
    admin_required,
    conseiller_or_admin_required
)
from insurance_web.backends import EmailBackend
from insurance_web.models import Profile


def dummy_view(request):
    from django.http import HttpResponse
    return HttpResponse("OK")


@pytest.mark.django_db
class TestDecorators:
    def setup_method(self):
        self.factory = RequestFactory()
    
    def _add_middleware(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        return request

    def test_conseiller_required_decorator(self):
        decorated_view = conseiller_required(dummy_view)
        
        conseiller_user = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller_user.profile.role = 'conseiller'
        conseiller_user.profile.save()
        
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin_user.profile.role = 'admin'
        admin_user.profile.save()
        
        normal_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        normal_user.profile.role = 'user'
        normal_user.profile.save()
        
        request = self.factory.get('/test/')
        request.user = conseiller_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 200, "Le conseiller devrait avoir accès"
        
        request = self.factory.get('/test/')
        request.user = admin_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 200, "L'admin devrait avoir accès"
        
        request = self.factory.get('/test/')
        request.user = normal_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 302, "Le user normal devrait être redirigé"
        assert response.url == '/', "La redirection devrait être vers home"
        
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 302, "L'utilisateur non authentifié devrait être redirigé"

    def test_admin_required_decorator(self):
        decorated_view = admin_required(dummy_view)
        
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin_user.profile.role = 'admin'
        admin_user.profile.save()
        
        conseiller_user = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller_user.profile.role = 'conseiller'
        conseiller_user.profile.save()
        
        normal_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        normal_user.profile.role = 'user'
        normal_user.profile.save()
        
        request = self.factory.get('/test/')
        request.user = admin_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 200, "L'admin devrait avoir accès"
        
        request = self.factory.get('/test/')
        request.user = conseiller_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 302, "Le conseiller devrait être redirigé"
        
        request = self.factory.get('/test/')
        request.user = normal_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 302, "Le user normal devrait être redirigé"
        
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 302, "L'utilisateur non authentifié devrait être redirigé"

    def test_conseiller_or_admin_required_decorator(self):
        decorated_view = conseiller_or_admin_required(dummy_view)
        
        conseiller_user = User.objects.create_user(
            username='conseiller',
            email='conseiller@example.com',
            password='testpass123'
        )
        conseiller_user.profile.role = 'conseiller'
        conseiller_user.profile.save()
        
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        admin_user.profile.role = 'admin'
        admin_user.profile.save()
        
        normal_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        normal_user.profile.role = 'user'
        normal_user.profile.save()
        
        request = self.factory.get('/test/')
        request.user = conseiller_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 200, "Le conseiller devrait avoir accès"
        
        request = self.factory.get('/test/')
        request.user = admin_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 200, "L'admin devrait avoir accès"
        
        request = self.factory.get('/test/')
        request.user = normal_user
        request = self._add_middleware(request)
        response = decorated_view(request)
        assert response.status_code == 302, "Le user normal devrait être redirigé"


@pytest.mark.django_db
class TestEmailBackend:
    def test_email_backend_authenticate_with_email(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )
        
        assert authenticated_user is not None, "L'utilisateur devrait être authentifié"
        assert authenticated_user == user, "L'utilisateur retourné devrait être le bon"

    def test_email_backend_authenticate_with_username(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='testuser',
            password='testpass123'
        )
        
        assert authenticated_user is not None, "L'utilisateur devrait être authentifié"
        assert authenticated_user == user, "L'utilisateur retourné devrait être le bon"

    def test_email_backend_authenticate_invalid_credentials(self):
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        backend = EmailBackend()
        
        authenticated_user = backend.authenticate(
            request=None,
            username='nonexistent@example.com',
            password='testpass123'
        )
        assert authenticated_user is None, "L'authentification devrait échouer avec un email inexistant"
        
        authenticated_user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='wrongpassword'
        )
        assert authenticated_user is None, "L'authentification devrait échouer avec un mot de passe incorrect"

    def test_email_backend_user_can_authenticate(self):
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='testpass123'
        )
        inactive_user.is_active = False
        inactive_user.save()
        
        backend = EmailBackend()
        authenticated_user = backend.authenticate(
            request=None,
            username='inactive@example.com',
            password='testpass123'
        )
        assert authenticated_user is None, \
            "L'authentification devrait échouer pour un utilisateur inactif"
        
        active_user = User.objects.create_user(
            username='active',
            email='active@example.com',
            password='testpass123'
        )
        active_user.is_active = True
        active_user.save()
        
        authenticated_user = backend.authenticate(
            request=None,
            username='active@example.com',
            password='testpass123'
        )
        assert authenticated_user is not None, \
            "L'authentification devrait réussir pour un utilisateur actif"
        assert authenticated_user == active_user, "L'utilisateur retourné devrait être le bon"

    def test_email_backend_case_sensitivity(self):
        user = User.objects.create_user(
            username='testuser',
            email='Test@Example.com',
            password='testpass123'
        )
        
        backend = EmailBackend()
        
        authenticated_user = backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )
