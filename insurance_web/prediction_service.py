import joblib
import os
from django.conf import settings
import numpy as np
import pandas as pd

MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'gb_pipeline.joblib')

_model = None

def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def calculate_insurance_premium(form_data):
    """
    Calcule la prime d'assurance en utilisant le modèle de régression.
    """
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