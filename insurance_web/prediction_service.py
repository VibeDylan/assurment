"""
Alias pour maintenir la compatibilité avec les imports existants.
Ce fichier redirige vers le nouveau module services.
"""
from .services.prediction_service import (
    calculate_insurance_premium,
    create_prediction,
    _load_model,
    MODEL_PATH,
    _model
)

__all__ = [
    'calculate_insurance_premium',
    'create_prediction',
    '_load_model',
    'MODEL_PATH',
    '_model',
]
