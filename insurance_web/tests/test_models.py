import pytest
from django.contrib.auth.models import User
from insurance_web.models import Profile


@pytest.mark.django_db
class TestProfileModel:

    def test_profile_creation(self):
        """
        Test 1: Vérifier qu'un Profile est créé automatiquement lors de la création d'un User
        - Vérifier les valeurs par défaut (role='user')
        - Vérifier les relations OneToOne avec User
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        assert hasattr(user, 'profile'), "Le Profile devrait être créé automatiquement"
        
        profile = user.profile
        assert Profile.objects.filter(user=user).exists(), "Le Profile devrait exister en base de données"
        
        assert profile.role == 'user', f"Le rôle par défaut devrait être 'user', mais c'est '{profile.role}'"
        
        assert user.profile == profile, "La relation OneToOne devrait fonctionner"
        
        profile_from_db = Profile.objects.get(user=user)
        assert profile == profile_from_db, "Le Profile devrait être le même objet"
        
        assert profile.user == user, "Le Profile devrait être lié au bon User"
        
        print("✅ Test réussi : Profile créé automatiquement avec rôle 'user' par défaut")

    def test_profile_str_method(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        profile = user.profile
        assert str(profile) == "Profile of Test User", "Le __str__ devrait retourner le bon format"
        print("✅ Test réussi : __str__ retourne le bon format")

    def test_profile_role_methods(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        