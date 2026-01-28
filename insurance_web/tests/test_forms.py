import pytest
from django.contrib.auth.models import User
from insurance_web.forms import CustomUserCreationForm, PredictionForm
from insurance_web.models import Profile


@pytest.mark.django_db
class TestCustomUserCreationForm:
    def test_form_valid_data(self):
        """Test que le formulaire accepte des données valides et crée un utilisateur"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        
        assert form.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form.errors}"
        
        user = form.save()
        assert user is not None, "L'utilisateur devrait être créé"
        assert User.objects.filter(email='john.doe@example.com').exists(), \
            "L'utilisateur devrait exister dans la base de données"
        
        saved_user = User.objects.get(email='john.doe@example.com')
        assert saved_user.first_name == 'John', "Le prénom devrait être correct"
        assert saved_user.last_name == 'Doe', "Le nom devrait être correct"
        assert saved_user.email == 'john.doe@example.com', "L'email devrait être correct"
        assert saved_user.check_password('securepass123'), "Le mot de passe devrait être correct"

    def test_form_email_validation(self):
        """Test la validation de l'email"""
        form_data_invalid = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalidemail',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data_invalid)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec un email sans @"
        assert 'email' in form.errors, "Il devrait y avoir une erreur sur le champ email"
        
        existing_user = User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )
        form_data_duplicate = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'existing@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data_duplicate)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec un email déjà existant"
        assert 'email' in form.errors, "Il devrait y avoir une erreur sur le champ email"
        assert 'already exists' in str(form.errors['email']).lower(), \
            "L'erreur devrait mentionner que l'email existe déjà"
        
        form_data_valid = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data_valid)
        assert form.is_valid(), f"Le formulaire devrait être valide avec un email valide. Erreurs: {form.errors}"

    def test_form_password_validation(self):
        """Test la validation des mots de passe"""
        form_data_short = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'short',
            'password2': 'short'
        }
        form = CustomUserCreationForm(data=form_data_short)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec un mot de passe < 8 caractères"
        assert 'password1' in form.errors, "Il devrait y avoir une erreur sur le champ password1"
        assert '8 characters' in str(form.errors['password1']).lower(), \
            "L'erreur devrait mentionner le minimum de 8 caractères"
        
        form_data_mismatch = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'securepass123',
            'password2': 'differentpass123'
        }
        form = CustomUserCreationForm(data=form_data_mismatch)
        assert not form.is_valid(), "Le formulaire devrait être invalide si les mots de passe ne correspondent pas"
        assert 'password2' in form.errors, "Il devrait y avoir une erreur sur le champ password2"
        assert 'match' in str(form.errors['password2']).lower(), \
            "L'erreur devrait mentionner que les mots de passe ne correspondent pas"
        
        form_data_valid = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data_valid)
        assert form.is_valid(), f"Le formulaire devrait être valide avec un mot de passe valide. Erreurs: {form.errors}"

    def test_form_username_generation(self):
        """Test la génération automatique du username depuis l'email"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert form.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form.errors}"
        
        user = form.save()
        assert user.username == 'john.doe', \
            f"Le username devrait être 'john.doe', mais est '{user.username}'"
        
        form_data2 = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'john.doe@test.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form2 = CustomUserCreationForm(data=form_data2)
        assert form2.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form2.errors}"
        
        user2 = form2.save()
        assert user2.username == 'john.doe1', \
            f"Le username devrait être 'john.doe1', mais est '{user2.username}'"
        
        form_data3 = {
            'first_name': 'Bob',
            'last_name': 'Doe',
            'email': 'john.doe@another.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form3 = CustomUserCreationForm(data=form_data3)
        assert form3.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form3.errors}"
        
        user3 = form3.save()
        assert user3.username == 'john.doe2', \
            f"Le username devrait être 'john.doe2', mais est '{user3.username}'"

    def test_form_required_fields(self):
        """Test que les champs requis sont bien validés"""
        form_data = {
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid(), "Le formulaire devrait être invalide sans first_name"
        assert 'first_name' in form.errors, "Il devrait y avoir une erreur sur le champ first_name"
        
        form_data = {
            'first_name': 'John',
            'email': 'john@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid(), "Le formulaire devrait être invalide sans last_name"
        assert 'last_name' in form.errors, "Il devrait y avoir une erreur sur le champ last_name"
        
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid(), "Le formulaire devrait être invalide sans email"
        assert 'email' in form.errors, "Il devrait y avoir une erreur sur le champ email"
        
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid(), "Le formulaire devrait être invalide sans password1"
        assert 'password1' in form.errors, "Il devrait y avoir une erreur sur le champ password1"
        
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert not form.is_valid(), "Le formulaire devrait être invalide sans password2"
        assert 'password2' in form.errors, "Il devrait y avoir une erreur sur le champ password2"

    def test_form_save_method(self):
        """Test que la méthode save() crée correctement un User et un Profile"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        assert form.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form.errors}"
        
        assert not User.objects.filter(email='john.doe@example.com').exists(), \
            "L'utilisateur ne devrait pas exister avant la sauvegarde"
        
        user = form.save()
        
        assert User.objects.filter(email='john.doe@example.com').exists(), \
            "L'utilisateur devrait être créé après la sauvegarde"
        
        assert hasattr(user, 'profile'), "L'utilisateur devrait avoir un profil"
        assert user.profile.role == 'user', \
            f"Le rôle du profil devrait être 'user' par défaut, mais est '{user.profile.role}'"
        
        saved_user = User.objects.get(email='john.doe@example.com')
        assert saved_user.first_name == 'John', "Le prénom devrait être correct"
        assert saved_user.last_name == 'Doe', "Le nom devrait être correct"
        assert saved_user.email == 'john.doe@example.com', "L'email devrait être correct"
        assert saved_user.username == 'john.doe', "Le username devrait être généré correctement"
        assert saved_user.check_password('securepass123'), "Le mot de passe devrait être correct"
        
        assert Profile.objects.filter(user=saved_user).exists(), \
            "Le profil devrait être créé pour l'utilisateur"


@pytest.mark.django_db
class TestPredictionForm:
    def test_form_valid_data(self):
        """Test que le formulaire accepte des données valides"""
        form_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 2,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data)
        
        assert form.is_valid(), f"Le formulaire devrait être valide. Erreurs: {form.errors}"
        
        assert form.cleaned_data['age'] == 30, "L'âge devrait être correct"
        assert form.cleaned_data['sex'] == 'male', "Le sexe devrait être correct"
        assert form.cleaned_data['bmi'] == 22.5, "Le BMI devrait être correct"
        assert form.cleaned_data['children'] == 2, "Le nombre d'enfants devrait être correct"
        assert form.cleaned_data['smoker'] == 'no', "Le statut fumeur devrait être correct"
        assert form.cleaned_data['region'] == 'northwest', "La région devrait être correcte"

    def test_form_age_validation(self):
        """Test la validation de l'âge"""
        form_data_invalid_low = {
            'age': 17,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_low)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec age < 18"
        assert 'age' in form.errors, "Il devrait y avoir une erreur sur le champ age"
        
        form_data_invalid_high = {
            'age': 101,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_high)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec age > 100"
        assert 'age' in form.errors, "Il devrait y avoir une erreur sur le champ age"
        
        form_data_valid_min = {
            'age': 18,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_min)
        assert form.is_valid(), f"Le formulaire devrait être valide avec age = 18. Erreurs: {form.errors}"
        
        form_data_valid_max = {
            'age': 100,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_max)
        assert form.is_valid(), f"Le formulaire devrait être valide avec age = 100. Erreurs: {form.errors}"
        
        form_data_valid = {
            'age': 45,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid)
        assert form.is_valid(), f"Le formulaire devrait être valide avec age entre 18 et 100. Erreurs: {form.errors}"

    def test_form_bmi_validation(self):
        """Test la validation du BMI"""
        form_data_invalid_low = {
            'age': 30,
            'sex': 'male',
            'bmi': 9.9,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_low)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec BMI < 10.0"
        assert 'bmi' in form.errors, "Il devrait y avoir une erreur sur le champ bmi"
        
        form_data_invalid_high = {
            'age': 30,
            'sex': 'male',
            'bmi': 50.1,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_high)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec BMI > 50.0"
        assert 'bmi' in form.errors, "Il devrait y avoir une erreur sur le champ bmi"
        
        form_data_valid_min = {
            'age': 30,
            'sex': 'male',
            'bmi': 10.0,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_min)
        assert form.is_valid(), f"Le formulaire devrait être valide avec BMI = 10.0. Erreurs: {form.errors}"
        
        form_data_valid_max = {
            'age': 30,
            'sex': 'male',
            'bmi': 50.0,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_max)
        assert form.is_valid(), f"Le formulaire devrait être valide avec BMI = 50.0. Erreurs: {form.errors}"
        
        form_data_valid = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid)
        assert form.is_valid(), f"Le formulaire devrait être valide avec BMI entre 10.0 et 50.0. Erreurs: {form.errors}"

    def test_form_children_validation(self):
        """Test la validation du nombre d'enfants"""
        form_data_invalid_low = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': -1,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_low)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec children < 0"
        assert 'children' in form.errors, "Il devrait y avoir une erreur sur le champ children"
        
        form_data_invalid_high = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 11,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_high)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec children > 10"
        assert 'children' in form.errors, "Il devrait y avoir une erreur sur le champ children"
        
        form_data_valid_min = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_min)
        assert form.is_valid(), f"Le formulaire devrait être valide avec children = 0. Erreurs: {form.errors}"
        
        form_data_valid_max = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 10,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_max)
        assert form.is_valid(), f"Le formulaire devrait être valide avec children = 10. Erreurs: {form.errors}"
        
        form_data_valid = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 3,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid)
        assert form.is_valid(), f"Le formulaire devrait être valide avec children entre 0 et 10. Erreurs: {form.errors}"

    def test_form_choice_fields(self):
        """Test la validation des champs de choix (sex, smoker, region)"""
        form_data_valid_male = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_male)
        assert form.is_valid(), f"Le formulaire devrait être valide avec sex='male'. Erreurs: {form.errors}"
        
        form_data_valid_female = {
            'age': 30,
            'sex': 'female',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_female)
        assert form.is_valid(), f"Le formulaire devrait être valide avec sex='female'. Erreurs: {form.errors}"
        
        form_data_invalid_sex = {
            'age': 30,
            'sex': 'invalid',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_sex)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec sex invalide"
        assert 'sex' in form.errors, "Il devrait y avoir une erreur sur le champ sex"
        
        form_data_valid_smoker_yes = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'yes',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_smoker_yes)
        assert form.is_valid(), f"Le formulaire devrait être valide avec smoker='yes'. Erreurs: {form.errors}"
        
        form_data_valid_smoker_no = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_valid_smoker_no)
        assert form.is_valid(), f"Le formulaire devrait être valide avec smoker='no'. Erreurs: {form.errors}"
        
        form_data_invalid_smoker = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'maybe',
            'region': 'northwest'
        }
        form = PredictionForm(data=form_data_invalid_smoker)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec smoker invalide"
        assert 'smoker' in form.errors, "Il devrait y avoir une erreur sur le champ smoker"
        
        valid_regions = ['northwest', 'northeast', 'southwest', 'southeast']
        for region in valid_regions:
            form_data_valid_region = {
                'age': 30,
                'sex': 'male',
                'bmi': 22.5,
                'children': 0,
                'smoker': 'no',
                'region': region
            }
            form = PredictionForm(data=form_data_valid_region)
            assert form.is_valid(), \
                f"Le formulaire devrait être valide avec region='{region}'. Erreurs: {form.errors}"
        
        form_data_invalid_region = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'invalid_region'
        }
        form = PredictionForm(data=form_data_invalid_region)
        assert not form.is_valid(), "Le formulaire devrait être invalide avec region invalide"
        assert 'region' in form.errors, "Il devrait y avoir une erreur sur le champ region"
