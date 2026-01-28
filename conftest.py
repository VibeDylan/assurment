"""
Configuration globale pour pytest
Ce fichier permet à pytest de fonctionner avec Django
"""
import os

# Set environment variable to indicate we're testing
os.environ['DJANGO_TESTING'] = '1'

# Configure Django settings pour les tests
# pytest-django fera le django.setup() automatiquement
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurement.settings')
