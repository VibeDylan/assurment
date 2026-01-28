import joblib
import os
from django.conf import settings
import pandas as pd 
from django.db import transaction

from django.utils.translation import gettext as _
from ..models import Prediction
from ..utils.logging import log_error, log_prediction, log_critical
from ..exceptions import (
    PredictionError,
    ModelNotFoundError,
    InvalidPredictionDataError,
)


MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'gb_pipeline.joblib')
_model = None


def _load_model():
    """Charge le modèle ML en cache"""
    global _model
    if _model is None:
        try:
            if not os.path.exists(MODEL_PATH):
                raise ModelNotFoundError(_("Model file not found at %(path)s") % {'path': MODEL_PATH})
            _model = joblib.load(MODEL_PATH)
        except FileNotFoundError:
            log_critical(_("Model file not found at %(path)s") % {'path': MODEL_PATH})
            raise ModelNotFoundError(_("Model file not found at %(path)s") % {'path': MODEL_PATH})
        except Exception as e:
            log_critical(_("Error loading model: %(error)s") % {'error': e}, exc_info=True)
            raise PredictionError(_("Failed to load prediction model: %(error)s") % {'error': e})
    return _model


def _validate_prediction_data(form_data):
    """Valide les données de prédiction"""
    required_fields = ['age', 'sex', 'bmi', 'children', 'smoker', 'region']
    missing_fields = [field for field in required_fields if field not in form_data]
    
    if missing_fields:
        raise InvalidPredictionDataError(_("Missing required fields: %(fields)s") % {'fields': missing_fields})
    
    if not (18 <= form_data['age'] <= 100):
        raise InvalidPredictionDataError(_("Age must be between 18 and 100"))
    
    if not (10.0 <= float(form_data['bmi']) <= 50.0):
        raise InvalidPredictionDataError(_("BMI must be between 10.0 and 50.0"))
    
    if form_data['sex'] not in ['male', 'female']:
        raise InvalidPredictionDataError(_("Sex must be 'male' or 'female'"))
    
    if form_data['smoker'] not in ['yes', 'no']:
        raise InvalidPredictionDataError(_("Smoker must be 'yes' or 'no'"))


def calculate_insurance_premium(form_data):
    """
    Calcule la prime d'assurance basée sur les données du formulaire.
    
    Args:
        form_data: Dictionnaire contenant les données du formulaire
        
    Returns:
        float: Montant de la prime prédite en euros
        
    Raises:
        InvalidPredictionDataError: Si les données sont invalides
        ModelNotFoundError: Si le modèle ML n'est pas trouvé
        PredictionError: Si une erreur survient lors du calcul
    """
    _validate_prediction_data(form_data)
    
    try:
        model = _load_model()
        data = {
            'age': [form_data['age']],
            'sex': [form_data['sex']],
            'bmi': [float(form_data['bmi'])],
            'children': [form_data['children']],
            'smoker': [form_data['smoker']],
            'region': [form_data['region']]
        }
        df = pd.DataFrame(data)
        prediction = model.predict(df)[0]
        return round(float(prediction), 2)
    except (InvalidPredictionDataError, ModelNotFoundError):
        raise
    except Exception as e:
        log_error(_("Error calculating insurance premium: %(error)s") % {'error': e}, exc_info=True, extra={
            'form_data': form_data
        })
        raise PredictionError(_("Failed to calculate insurance premium: %(error)s") % {'error': e})


@transaction.atomic
def create_prediction(user, created_by, form_data, predicted_amount):
    """
    Crée une prédiction et met à jour le profil utilisateur.
    
    Args:
        user: Utilisateur pour qui la prédiction est créée
        created_by: Utilisateur qui a créé la prédiction
        form_data: Données du formulaire
        predicted_amount: Montant prédit
        
    Returns:
        Prediction: Instance de prédiction créée
        
    Raises:
        PredictionError: Si une erreur survient lors de la création
    """
    if not user or not hasattr(user, 'profile'):
        raise PredictionError(_("User must have a profile"))
    
    try:
        prediction = Prediction.objects.create(
            user=user,
            created_by=created_by,
            predicted_amount=predicted_amount,
            **form_data
        )
        
        profile = user.profile
        for key, value in form_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.save()
        
        log_prediction(created_by, predicted_amount, form_data)
        
        return prediction
    except Exception as e:
        log_error(
            _("Error creating prediction for user %(id)s: %(error)s") % {'id': user.id, 'error': e},
            exc_info=True,
            extra={'user_id': user.id, 'created_by_id': created_by.id}
        )
        raise PredictionError(_("Failed to create prediction: %(error)s") % {'error': e})
