import pytest
import os
import joblib
import importlib
from django.conf import settings
from insurance_web.services import prediction_service
from insurance_web.services.prediction_service import (
    _load_model,
    calculate_insurance_premium,
    MODEL_PATH
)


@pytest.mark.django_db
class TestPredictionService:
    def test_model_file_exists(self):
        assert os.path.exists(MODEL_PATH), \
            f"Le fichier modèle devrait exister à {MODEL_PATH}"
        assert os.path.isfile(MODEL_PATH), \
            f"{MODEL_PATH} devrait être un fichier"

    def test_load_model(self):
        original_model = prediction_service._model
        
        prediction_service._model = None
        
        try:
            model = _load_model()
            
            assert model is not None, "Le modèle devrait être chargé"
            
            assert prediction_service._model is not None, \
                "Le modèle devrait être mis en cache dans _model"
            assert prediction_service._model == model, \
                "Le modèle retourné devrait être le même que celui en cache"
            
            model2 = _load_model()
            assert model2 is model, "Le modèle devrait être le même objet (cache)"
            
        finally:
            prediction_service._model = original_model

    def test_calculate_insurance_premium(self):
        form_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        
        result = calculate_insurance_premium(form_data)
        
        assert isinstance(result, float), f"Le résultat devrait être un float, mais est {type(result)}"
        
        decimal_places = len(str(result).split('.')[-1]) if '.' in str(result) else 0
        assert decimal_places <= 2, \
            f"Le résultat devrait être arrondi à 2 décimales, mais a {decimal_places} décimales"
        
        assert result > 0, f"Le résultat devrait être positif, mais est {result}"

    def test_calculate_insurance_premium_with_different_inputs(self):
        base_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        
        base_result = calculate_insurance_premium(base_data)
        
        data_age_young = base_data.copy()
        data_age_young['age'] = 18
        result_young = calculate_insurance_premium(data_age_young)
        
        data_age_old = base_data.copy()
        data_age_old['age'] = 60
        result_old = calculate_insurance_premium(data_age_old)
        
        assert isinstance(result_young, float), "Le résultat pour age=18 devrait être un float"
        assert isinstance(result_old, float), "Le résultat pour age=60 devrait être un float"
        
        data_female = base_data.copy()
        data_female['sex'] = 'female'
        result_female = calculate_insurance_premium(data_female)
        
        assert isinstance(result_female, float), "Le résultat pour sex=female devrait être un float"
        
        data_smoker = base_data.copy()
        data_smoker['smoker'] = 'yes'
        result_smoker = calculate_insurance_premium(data_smoker)
        
        assert isinstance(result_smoker, float), "Le résultat pour smoker=yes devrait être un float"
        
        data_bmi_low = base_data.copy()
        data_bmi_low['bmi'] = 18.0
        result_bmi_low = calculate_insurance_premium(data_bmi_low)
        
        data_bmi_high = base_data.copy()
        data_bmi_high['bmi'] = 35.0
        result_bmi_high = calculate_insurance_premium(data_bmi_high)
        
        assert isinstance(result_bmi_low, float), "Le résultat pour bmi=18.0 devrait être un float"
        assert isinstance(result_bmi_high, float), "Le résultat pour bmi=35.0 devrait être un float"
        
        data_children = base_data.copy()
        data_children['children'] = 3
        result_children = calculate_insurance_premium(data_children)
        
        assert isinstance(result_children, float), "Le résultat pour children=3 devrait être un float"
        
        regions = ['northwest', 'northeast', 'southwest', 'southeast']
        results_by_region = {}
        for region in regions:
            data_region = base_data.copy()
            data_region['region'] = region
            results_by_region[region] = calculate_insurance_premium(data_region)
            assert isinstance(results_by_region[region], float), \
                f"Le résultat pour region={region} devrait être un float"

    def test_prediction_edge_cases(self):
        form_data_min_age = {
            'age': 18,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        result_min_age = calculate_insurance_premium(form_data_min_age)
        assert isinstance(result_min_age, float), "Le résultat pour age=18 devrait être un float"
        assert result_min_age > 0, "Le résultat devrait être positif"
        
        form_data_max_age = {
            'age': 100,
            'sex': 'male',
            'bmi': 22.5,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        result_max_age = calculate_insurance_premium(form_data_max_age)
        assert isinstance(result_max_age, float), "Le résultat pour age=100 devrait être un float"
        assert result_max_age > 0, "Le résultat devrait être positif"
        
        form_data_min_bmi = {
            'age': 30,
            'sex': 'male',
            'bmi': 10.0,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        result_min_bmi = calculate_insurance_premium(form_data_min_bmi)
        assert isinstance(result_min_bmi, float), "Le résultat pour bmi=10.0 devrait être un float"
        assert result_min_bmi > 0, "Le résultat devrait être positif"
        
        form_data_max_bmi = {
            'age': 30,
            'sex': 'male',
            'bmi': 50.0,
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        result_max_bmi = calculate_insurance_premium(form_data_max_bmi)
        assert isinstance(result_max_bmi, float), "Le résultat pour bmi=50.0 devrait être un float"
        assert result_max_bmi > 0, "Le résultat devrait être positif"
