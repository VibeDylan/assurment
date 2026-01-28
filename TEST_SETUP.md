# Guide de Configuration des Tests

> **Note** : Si votre projet est lancé avec Docker, consultez [DOCKER_TESTING.md](DOCKER_TESTING.md) pour les instructions spécifiques à Docker.

## Problèmes courants et solutions

### 1. Dépendances manquantes

Si vous voyez des erreurs comme `ModuleNotFoundError: No module named 'joblib'` :

```bash
# Activer votre environnement virtuel
source .venv/bin/activate

# Installer toutes les dépendances
pip install -r requirements.txt
```

### 2. Exécuter les tests

#### Option A : Avec pytest (recommandé)

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances si pas déjà fait
pip install -r requirements.txt

# Exécuter le test spécifique
pytest insurance_web/tests/test.models.py::TestProfileModel::test_profile_creation -v

# Ou tous les tests du fichier
pytest insurance_web/tests/test.models.py -v

# Ou tous les tests
pytest
```

#### Option B : Avec Django test runner

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances si pas déjà fait
pip install -r requirements.txt

# Exécuter le test
python manage.py test insurance_web.tests.test_models.TestProfileModel.test_profile_creation

# Ou tous les tests
python manage.py test
```

### 3. Si pytest ne trouve pas le module

Si vous voyez `ImportError: No module named 'assurment'` :

1. Vérifiez que vous êtes dans le répertoire racine du projet
2. Vérifiez que `pytest.ini` contient bien `DJANGO_SETTINGS_MODULE = assurement.settings`
3. Essayez de nettoyer le cache pytest :
   ```bash
   rm -rf .pytest_cache
   rm -rf __pycache__
   find . -type d -name __pycache__ -exec rm -r {} +
   ```

### 4. Vérification rapide

Pour vérifier que tout est bien configuré :

```bash
# 1. Vérifier que vous êtes dans le bon répertoire
pwd  # Devrait afficher .../assurement

# 2. Vérifier que le venv est activé
which python  # Devrait pointer vers .venv/bin/python

# 3. Vérifier que les dépendances sont installées
pip list | grep -E "pytest|django|joblib"

# 4. Tester l'import Django
python -c "import django; print(django.get_version())"
```

## Commandes utiles

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Exécuter tous les tests avec coverage
coverage run -m pytest
coverage report
coverage html  # Génère un rapport HTML dans htmlcov/

# Exécuter les tests en mode verbose
pytest -v

# Exécuter les tests avec sortie détaillée en cas d'erreur
pytest -vv --tb=long
```
