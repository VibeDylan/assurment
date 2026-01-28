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

        assert user.profile.is_user(), "Le profil devrait être un utilisateur"
        assert not user.profile.is_conseiller(), "Le profil ne devrait pas être un conseiller"
        assert not user.profile.is_admin(), "Le profil ne devrait pas être un administrateur"
        print("✅ Test réussi : Méthodes de rôle fonctionnent correctement")

    def test_profile_permission_methods(self):
        user_normal = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User'
        )
        
        assert user_normal.profile.role == 'user', "Le rôle par défaut devrait être 'user'"
        
        assert not user_normal.profile.can_make_prediction_for_others(), "Un user normal ne devrait PAS pouvoir faire des prédictions pour d'autres"
        assert not user_normal.profile.can_view_calendar(), "Un user normal ne devrait PAS pouvoir voir le calendrier"
        assert not user_normal.profile.can_view_all_profiles(), "Un user normal ne devrait PAS pouvoir voir tous les profils"
        
        user_conseiller = User.objects.create_user(
            username='conseilleruser',
            email='conseiller@example.com',
            password='testpass123',
            first_name='Conseiller',
            last_name='User'
        )
        user_conseiller.profile.role = 'conseiller'
        user_conseiller.profile.save()
        
        assert user_conseiller.profile.role == 'conseiller', "Le rôle devrait être 'conseiller'"
        
        assert user_conseiller.profile.can_make_prediction_for_others(), "Un conseiller DEVRAIT pouvoir faire des prédictions pour d'autres"
        assert user_conseiller.profile.can_view_calendar(), "Un conseiller DEVRAIT pouvoir voir le calendrier"
        assert user_conseiller.profile.can_view_all_profiles(), "Un conseiller DEVRAIT pouvoir voir tous les profils"
        
        user_admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        user_admin.profile.role = 'admin'
        user_admin.profile.save()
        
        assert user_admin.profile.role == 'admin', "Le rôle devrait être 'admin'"
        
        assert user_admin.profile.can_make_prediction_for_others(), "Un admin DEVRAIT pouvoir faire des prédictions pour d'autres"
        assert user_admin.profile.can_view_calendar(), "Un admin DEVRAIT pouvoir voir le calendrier"
        assert user_admin.profile.can_view_all_profiles(), "Un admin DEVRAIT pouvoir voir tous les profils"
                
    def test_profile_field_constraints(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        assert user.profile.age is None, "L'âge devrait être None"
        assert user.profile.sex is None, "Le sexe devrait être None"
        assert user.profile.bmi is None, "Le BMI devrait être None"