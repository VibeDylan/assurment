# Guide Complet des Tests - Assurement

Ce document décrit tous les tests nécessaires pour l'application Assurement, organisés par type et priorité.

## 📋 Table des Matières

1. [Tests Unitaires](#tests-unitaires)
2. [Tests d'Intégration](#tests-dintégration)
3. [Tests End-to-End](#tests-end-to-end)
4. [Tests de Sécurité](#tests-de-sécurité)
5. [Tests de Performance](#tests-de-performance)
6. [Configuration des Tests](#configuration-des-tests)

---

## 🧪 Tests Unitaires



#### PredictionForm
```python
# Tests à créer :

1. test_form_valid_data()
   - Tester avec toutes les données valides
   - Vérifier is_valid() = True

2. test_form_age_validation()
   - Tester age < 18 (doit échouer)
   - Tester age > 100 (doit échouer)
   - Tester age entre 18 et 100 (valide)

3. test_form_bmi_validation()
   - Tester BMI < 10.0 (doit échouer)
   - Tester BMI > 50.0 (doit échouer)
   - Tester BMI valide

4. test_form_children_validation()
   - Tester children < 0 (doit échouer)
   - Tester children > 10 (doit échouer)
   - Tester children valide

5. test_form_choice_fields()
   - Tester sex avec choix valides
   - Tester smoker avec choix valides
   - Tester region avec choix valides
   - Tester avec valeurs invalides
```

#### AppointmentForm
```python
# Tests à créer :

1. test_form_valid_data()
   - Tester avec date_time future valide
   - Tester avec duration_minutes valide

2. test_form_date_time_validation()
   - Tester date_time dans le passé (doit échouer)
   - Tester date_time future (valide)

3. test_form_duration_validation()
   - Tester duration < 15 minutes (doit échouer)
   - Tester duration > 240 minutes (doit échouer)
   - Tester duration valide

4. test_form_notes_optional()
   - Vérifier que notes est optionnel
   - Tester avec notes vide
   - Tester avec notes rempli
```

#### AdminUserManagementForm
```python
# Tests à créer :

1. test_form_valid_data()
   - Tester création d'utilisateur avec tous les champs
   - Vérifier que save() crée User et Profile

2. test_form_email_uniqueness()
   - Tester email déjà existant (doit échouer)

3. test_form_role_assignment()
   - Vérifier que le rôle est correctement assigné au Profile
   - Tester tous les rôles possibles

4. test_form_password_validation()
   - Tester mot de passe < 8 caractères
```

#### AdminUserRoleForm
```python
# Tests à créer :

1. test_form_valid_role()
   - Tester avec tous les rôles valides
   - Vérifier is_valid() = True

2. test_form_invalid_role()
   - Tester avec rôle invalide
```

### 3. Tests des Services (`insurance_web/tests/test_services.py`)

#### prediction_service.py
```python
# Tests à créer :

1. test_load_model()
   - Vérifier que le modèle est chargé correctement
   - Vérifier que le modèle est mis en cache (_model global)
   - Vérifier que le chargement ne se fait qu'une fois

2. test_calculate_insurance_premium()
   - Tester avec des données valides
   - Vérifier que le résultat est un float
   - Vérifier que le résultat est arrondi à 2 décimales
   - Vérifier que le résultat est positif

3. test_calculate_insurance_premium_with_different_inputs()
   - Tester avec différents âges
   - Tester avec différents sexes
   - Tester avec différents BMI
   - Tester avec fumeur/non-fumeur
   - Vérifier que les résultats varient selon les inputs

4. test_model_file_exists()
   - Vérifier que le fichier model existe
   - Tester gestion d'erreur si fichier manquant

5. test_prediction_edge_cases()
   - Tester avec age minimum (18)
   - Tester avec age maximum (100)
   - Tester avec BMI minimum (10.0)
   - Tester avec BMI maximum (50.0)
```

### 4. Tests des Utilitaires (`insurance_web/tests/test_utils.py`)

#### decorators.py
```python
# Tests à créer :

1. test_conseiller_required_decorator()
   - Tester accès autorisé pour conseiller
   - Tester accès autorisé pour admin
   - Tester accès refusé pour user normal
   - Tester redirection si non authentifié
   - Vérifier message d'erreur approprié

2. test_admin_required_decorator()
   - Tester accès autorisé pour admin
   - Tester accès refusé pour conseiller
   - Tester accès refusé pour user normal
   - Tester redirection si non authentifié
   - Vérifier message d'erreur approprié

3. test_conseiller_or_admin_required_decorator()
   - Tester accès autorisé pour conseiller
   - Tester accès autorisé pour admin
   - Tester accès refusé pour user normal
```

#### backends.py
```python
# Tests à créer :

1. test_email_backend_authenticate_with_email()
   - Authentifier avec email valide
   - Vérifier que l'utilisateur est retourné

2. test_email_backend_authenticate_with_username()
   - Authentifier avec username valide
   - Vérifier que l'utilisateur est retourné

3. test_email_backend_authenticate_invalid_credentials()
   - Tester avec email inexistant
   - Tester avec mot de passe incorrect
   - Vérifier que None est retourné

4. test_email_backend_user_can_authenticate()
   - Tester avec user.is_active = False (doit échouer)
   - Tester avec user.is_active = True (doit réussir)

5. test_email_backend_case_sensitivity()
   - Tester si email est case-sensitive ou non
```

---

## 🔗 Tests d'Intégration

### 5. Tests des Vues (`insurance_web/tests/test_views.py`)

#### User Views
```python
# Tests à créer :

1. test_home_view()
   - Accès GET à la page d'accueil
   - Vérifier template utilisé
   - Vérifier status_code = 200

2. test_signup_view_get()
   - Accès GET au formulaire d'inscription
   - Vérifier que le formulaire est présent

3. test_signup_view_post_valid()
   - POST avec données valides
   - Vérifier création de User
   - Vérifier création de Profile
   - Vérifier redirection vers home
   - Vérifier que l'utilisateur est connecté

4. test_signup_view_post_invalid()
   - POST avec données invalides
   - Vérifier que le formulaire contient des erreurs
   - Vérifier que User n'est pas créé

5. test_login_view()
   - Tester connexion avec email
   - Tester connexion avec username
   - Vérifier redirection après connexion

6. test_logout_view()
   - Tester déconnexion
   - Vérifier redirection vers home

7. test_profile_view()
   - Tester accès au profil (login requis)
   - Vérifier affichage des prédictions
   - Tester pagination des prédictions

8. test_predict_view_get()
   - Tester accès GET (login requis)
   - Vérifier pré-remplissage avec données du profil

9. test_predict_view_post()
   - POST avec données valides
   - Vérifier création de Prediction
   - Vérifier mise à jour du Profile
   - Vérifier message de succès

10. test_conseillers_list_view()
    - Tester affichage de la liste des conseillers
    - Vérifier que seuls les conseillers sont affichés

11. test_conseiller_availability_view()
    - Tester affichage des disponibilités
    - Tester calcul des créneaux disponibles
    - Tester filtrage par date

12. test_create_appointment_view()
    - Tester création de rendez-vous valide
    - Tester conflit de créneaux
    - Tester date dans le passé (doit échouer)
    - Vérifier création de Appointment

13. test_my_appointments_view()
    - Tester affichage des rendez-vous futurs
    - Tester affichage des rendez-vous passés
    - Vérifier que seuls les rendez-vous du user sont affichés
```

#### Conseiller Views
```python
# Tests à créer :

1. test_conseiller_dashboard_view()
   - Tester accès avec rôle conseiller
   - Tester accès avec rôle admin
   - Tester refus d'accès pour user normal
   - Vérifier statistiques affichées
   - Vérifier que admin voit tous les rendez-vous
   - Vérifier que conseiller voit seulement ses rendez-vous

2. test_conseiller_predict_for_client_view()
   - Tester prédiction pour un client spécifique
   - Tester prédiction sans client (nouveau)
   - Vérifier création de Prediction avec created_by correct
   - Vérifier mise à jour du profil client

3. test_conseiller_calendar_view()
   - Tester affichage du calendrier
   - Tester navigation mois précédent/suivant
   - Vérifier que admin voit tous les rendez-vous
   - Vérifier que conseiller voit seulement ses rendez-vous
   - Tester calcul des jours du calendrier

4. test_conseiller_clients_list_view()
   - Tester liste des clients avec rendez-vous
   - Tester liste de tous les utilisateurs
   - Vérifier que admin voit tous les utilisateurs
   - Vérifier que conseiller ne voit pas les admins
```

#### Admin Views
```python
# Tests à créer :

1. test_admin_dashboard_view()
   - Tester accès avec rôle admin
   - Tester refus d'accès pour autres rôles
   - Vérifier statistiques affichées
   - Tester création d'utilisateur via formulaire

2. test_admin_user_management_view()
   - Tester affichage de tous les utilisateurs
   - Vérifier tri par date_joined
   - Vérifier select_related pour performance

3. test_admin_change_user_role_view()
   - Tester changement de rôle valide
   - Tester tentative de modifier son propre rôle (doit échouer)
   - Vérifier message de succès
   - Vérifier redirection

4. test_admin_toggle_user_status_view()
   - Tester activation d'un compte
   - Tester désactivation d'un compte
   - Tester tentative de modifier son propre statut (doit échouer)
   - Vérifier message de succès

5. test_admin_delete_user_view_get()
   - Tester affichage de la page de confirmation
   - Vérifier informations utilisateur affichées

6. test_admin_delete_user_view_post()
   - Tester suppression d'utilisateur
   - Vérifier suppression en cascade du Profile
   - Tester tentative de supprimer son propre compte (doit échouer)
   - Vérifier message de succès
```

---

## 🎯 Tests End-to-End

### 6. Tests de Workflows Complets (`insurance_web/tests/test_e2e.py`)

```python
# Tests à créer :

1. test_user_registration_workflow()
   - Inscription → Connexion automatique → Accès au profil
   - Vérifier création de User et Profile
   - Vérifier redirection correcte

2. test_prediction_workflow()
   - Connexion → Prédiction → Vérification dans l'historique
   - Vérifier que Prediction est créée
   - Vérifier que Profile est mis à jour
   - Vérifier affichage dans le profil

3. test_appointment_booking_workflow()
   - Connexion → Liste conseillers → Disponibilités → Création rendez-vous
   - Vérifier création de Appointment
   - Vérifier que le créneau n'est plus disponible
   - Vérifier affichage dans "Mes rendez-vous"

4. test_conseiller_client_management_workflow()
   - Connexion conseiller → Liste clients → Prédiction pour client
   - Vérifier que la prédiction est associée au bon client
   - Vérifier que created_by est le conseiller

5. test_admin_user_management_workflow()
   - Connexion admin → Création utilisateur → Changement rôle → Suppression
   - Vérifier toutes les étapes fonctionnent
   - Vérifier messages de succès/erreur

6. test_role_based_access_workflow()
   - Tester accès aux différentes sections selon le rôle
   - User : accès limité
   - Conseiller : accès conseiller + user
   - Admin : accès admin + conseiller + user
```

---

## 🔒 Tests de Sécurité

### 7. Tests de Sécurité (`insurance_web/tests/test_security.py`)

```python
# Tests à créer :

1. test_authentication_required()
   - Tester que les vues protégées redirigent si non authentifié
   - Tester toutes les vues avec @login_required

2. test_permission_checks()
   - Tester que conseiller_required bloque les users normaux
   - Tester que admin_required bloque les conseillers et users
   - Vérifier messages d'erreur appropriés

3. test_csrf_protection()
   - Tester que les formulaires POST nécessitent CSRF token
   - Tester POST sans token (doit échouer)

4. test_user_isolation()
   - Vérifier qu'un user ne peut pas voir les données d'un autre user
   - Tester accès aux prédictions d'autres users
   - Tester accès aux rendez-vous d'autres users

5. test_admin_self_protection()
   - Vérifier qu'un admin ne peut pas modifier son propre rôle
   - Vérifier qu'un admin ne peut pas modifier son propre statut
   - Vérifier qu'un admin ne peut pas supprimer son propre compte

6. test_sql_injection_protection()
   - Tester entrées avec caractères SQL spéciaux
   - Vérifier que Django ORM échappe correctement

7. test_xss_protection()
   - Tester entrées avec scripts JavaScript
   - Vérifier que le contenu est échappé dans les templates

8. test_password_hashing()
   - Vérifier que les mots de passe sont hashés (pas en clair)
   - Vérifier que check_password fonctionne correctement

9. test_email_uniqueness()
   - Vérifier qu'on ne peut pas créer deux users avec le même email
   - Tester au niveau formulaire et modèle
```

---

## ⚡ Tests de Performance

### 8. Tests de Performance (`insurance_web/tests/test_performance.py`)

```python
# Tests à créer :

1. test_model_query_optimization()
   - Tester que select_related est utilisé pour Profile
   - Vérifier nombre de requêtes SQL (avec django-debug-toolbar ou assertNumQueries)

2. test_pagination_performance()
   - Tester pagination avec beaucoup de données
   - Vérifier que seulement 10 prédictions sont chargées par page

3. test_model_caching()
   - Vérifier que le modèle ML est mis en cache
   - Tester que le chargement ne se fait qu'une fois

4. test_bulk_operations()
   - Tester création de plusieurs utilisateurs en batch
   - Vérifier performance acceptable
```

---

## ⚙️ Configuration des Tests

### Structure des fichiers de test

```
insurance_web/
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # Tests des modèles
│   ├── test_forms.py           # Tests des formulaires
│   ├── test_services.py        # Tests des services
│   ├── test_utils.py           # Tests des utilitaires
│   ├── test_views.py           # Tests d'intégration des vues
│   ├── test_e2e.py             # Tests end-to-end
│   ├── test_security.py        # Tests de sécurité
│   ├── test_performance.py     # Tests de performance
│   └── factories.py            # Factories pour créer des données de test
```

### Configuration Django pour les tests

Dans `settings.py`, créer un fichier `test_settings.py` ou utiliser des variables d'environnement :

```python
# Pour les tests, utiliser une base de données en mémoire SQLite
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }
```

### Utilisation de Factories (optionnel mais recommandé)

Créer `insurance_web/tests/factories.py` avec `factory_boy` :

```python
import factory
from django.contrib.auth.models import User
from insurance_web.models import Profile, Appointment, Prediction

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
    
    user = factory.SubFactory(UserFactory)
    role = 'user'
    # ... autres champs
```

### Commandes pour exécuter les tests

```bash
# Tous les tests
python manage.py test

# Tests spécifiques
python manage.py test insurance_web.tests.test_models
python manage.py test insurance_web.tests.test_views.TestUserViews

# Avec verbosité
python manage.py test --verbosity=2

# Avec couverture de code (nécessite coverage)
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère un rapport HTML

# Tests en parallèle (Django 3.1+)
python manage.py test --parallel
```

### Outils recommandés

1. **pytest-django** : Alternative à unittest avec meilleure syntaxe
2. **factory_boy** : Création facile de données de test
3. **coverage** : Mesure de la couverture de code
4. **django-debug-toolbar** : Debug des requêtes SQL (dev uniquement)
5. **model-bakery** : Alternative à factory_boy

### Installation des outils

```bash
`pip install pytest pytest-django factory-boy coverage model-bakery`
```

### Exemple de test avec pytest

```python
import pytest
from django.test import Client
from insurance_web.models import User, Profile

@pytest.mark.django_db
def test_user_signup():
    client = Client()
    response = client.post('/signup/', {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@test.com',
        'password1': 'testpass123',
        'password2': 'testpass123'
    })
    assert response.status_code == 302  # Redirection
    assert User.objects.filter(email='john@test.com').exists()
    assert Profile.objects.filter(user__email='john@test.com').exists()
```

---

## 📊 Métriques de Couverture Cible

- **Modèles** : 100% de couverture
- **Formulaires** : 95%+ de couverture
- **Vues** : 80%+ de couverture (toutes les routes principales)
- **Services** : 100% de couverture
- **Utilitaires** : 100% de couverture

---

## ✅ Checklist de Tests Prioritaires

### Priorité 1 (Critique - À faire en premier)
- [ ] Tests des modèles (Profile, Appointment, Prediction)
- [ ] Tests de sécurité (authentification, permissions)
- [ ] Tests des formulaires (validation)
- [ ] Tests du service de prédiction

### Priorité 2 (Important)
- [ ] Tests d'intégration des vues principales
- [ ] Tests des décorateurs de permissions
- [ ] Tests du backend d'authentification
- [ ] Tests end-to-end des workflows critiques

### Priorité 3 (Recommandé)
- [ ] Tests de performance
- [ ] Tests de tous les cas limites
- [ ] Tests de l'interface admin
- [ ] Tests de pagination

---

## 📝 Notes Importantes

1. **Utiliser des fixtures** : Créer des données de test réutilisables
2. **Isolation** : Chaque test doit être indépendant
3. **Nettoyage** : Django nettoie automatiquement la DB entre les tests
4. **Mocking** : Utiliser des mocks pour les appels externes (API, fichiers)
5. **Fixtures JSON** : Pour les données complexes, utiliser `dumpdata` et `loaddata`

### Exemple de fixture

```bash
# Créer des données de test
python manage.py dumpdata insurance_web --indent 2 > insurance_web/tests/fixtures/test_data.json

# Utiliser dans les tests
@pytest.mark.django_db
@pytest.mark.usefixtures('load_test_data')
def test_something():
    ...
```

---

Ce guide vous donne une vue complète de tous les tests à implémenter. Commencez par les tests de Priorité 1, puis progressez vers les autres selon vos besoins.
