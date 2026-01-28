# Améliorations de l'Architecture - Plan de Refactorisation

## 🔍 Problèmes Identifiés

### 1. **Fichier `cbv_views.py` trop volumineux** (545 lignes, 18 classes)
   - Toutes les vues sont dans un seul fichier
   - Difficile à maintenir et naviguer
   - Violation du principe de responsabilité unique

### 2. **Fichier `forms.py` trop volumineux** (297 lignes)
   - Tous les formulaires dans un seul fichier
   - Mélange de différents domaines (auth, prediction, admin)

### 3. **Choix de modèles définis dans les modèles**
   - `SEX_CHOICES`, `SMOKER_CHOICES`, `REGION_CHOICES`, `ROLE_CHOICES` dans `models.py`
   - Devrait être dans un fichier `constants.py` pour réutilisation

### 4. **Logique métier dans les vues**
   - Calculs et logique métier directement dans les vues
   - Pas de couche service séparée

### 5. **Pas de séparation par domaine**
   - Vues utilisateur, conseiller et admin mélangées

## ✅ Solutions Proposées

### 1. Séparer les vues par domaine

```
insurance_web/
├── views/
│   ├── __init__.py
│   ├── base.py              # Vues de base (HomeView, LogoutView)
│   ├── user_views.py        # Vues utilisateur (ProfileView, PredictView, etc.)
│   ├── conseiller_views.py  # Vues conseiller
│   └── admin_views.py       # Vues admin
```

### 2. Créer un fichier `constants.py`

```python
# insurance_web/constants.py
SEX_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]

SMOKER_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

REGION_CHOICES = [
    ('northwest', 'Northwest'),
    ('northeast', 'Northeast'),
    ('southwest', 'Southwest'),
    ('southeast', 'Southeast'),
]

ROLE_CHOICES = [
    ('user', 'User'),
    ('conseiller', 'Advisor'),
    ('admin', 'Administrator'),
]
```

### 3. Séparer les formulaires par domaine

```
insurance_web/
├── forms/
│   ├── __init__.py
│   ├── auth_forms.py        # CustomUserCreationForm
│   ├── prediction_forms.py  # PredictionForm
│   ├── appointment_forms.py # AppointmentForm
│   └── admin_forms.py       # AdminUserManagementForm, AdminUserRoleForm
```

### 4. Créer une couche service

```
insurance_web/
├── services/
│   ├── __init__.py
│   ├── prediction_service.py  # Déjà existant, améliorer
│   ├── appointment_service.py # Logique métier pour les rendez-vous
│   └── user_service.py         # Logique métier pour les utilisateurs
```

### 5. Créer un fichier `permissions.py`

```python
# insurance_web/permissions.py
from django.core.exceptions import PermissionDenied

def check_conseiller_permission(user):
    if not user.is_authenticated or not user.profile.is_conseiller():
        raise PermissionDenied

def check_admin_permission(user):
    if not user.is_authenticated or not user.profile.is_admin():
        raise PermissionDenied
```

## 📋 Plan d'Action

### Phase 1 : Créer la structure de base
1. ✅ Créer `constants.py`
2. ✅ Créer le dossier `services/`
3. ✅ Créer le dossier `forms/`

### Phase 2 : Refactoriser les modèles
1. ✅ Déplacer les choix vers `constants.py`
2. ✅ Mettre à jour les imports dans `models.py`

### Phase 3 : Refactoriser les formulaires
1. ✅ Séparer `forms.py` en modules par domaine
2. ✅ Mettre à jour les imports dans les vues

### Phase 4 : Refactoriser les vues
1. ✅ Séparer `cbv_views.py` en modules par domaine
2. ✅ Mettre à jour `urls.py`

### Phase 5 : Créer les services
1. ✅ Extraire la logique métier des vues vers les services
2. ✅ Mettre à jour les vues pour utiliser les services

## 🎯 Bénéfices Attendus

- ✅ **Maintenabilité** : Code plus facile à comprendre et modifier
- ✅ **Testabilité** : Services isolés plus faciles à tester
- ✅ **Réutilisabilité** : Logique métier réutilisable
- ✅ **Séparation des responsabilités** : Chaque module a un rôle clair
- ✅ **Scalabilité** : Plus facile d'ajouter de nouvelles fonctionnalités
