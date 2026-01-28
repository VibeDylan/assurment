import joblib
import os
from django.conf import settings
import pandas as pd
from django.utils import timezone

from ..models import Prediction


MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'gb_pipeline.joblib')
_model = None


def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def calculate_insurance_premium(form_data):
    """Calcule la prime d'assurance basée sur les données du formulaire"""
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


def create_prediction(user, created_by, form_data, predicted_amount):
    """Crée une prédiction et met à jour le profil utilisateur"""
    prediction = Prediction.objects.create(
        user=user,
        created_by=created_by,
        predicted_amount=predicted_amount,
        **form_data
    )
    
    if user and user.profile:
        profile = user.profile
        for key, value in form_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.save()
    
    return prediction
