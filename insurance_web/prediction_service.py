"""
Service de prédiction de prime d'assurance.
Ce module contient la logique de calcul de la prime d'assurance basée sur les champs standards.
"""
import math


def calculate_insurance_premium(form_data):
    """
    Calcule la prime d'assurance basée sur les données du formulaire.
    
    Formule basée sur les facteurs de risque standards :
    - age: facteur de risque selon l'âge
    - sex: différence homme/femme
    - bmi: indice de masse corporelle
    - children: nombre d'enfants
    - smoker: facteur de risque majeur
    - region: facteur géographique
    
    Args:
        form_data: Dictionnaire contenant les données du formulaire
        
    Returns:
        float: Montant de la prime d'assurance en euros
    """
    base_premium = 1000.0
    
    age = form_data['age']
    sex = form_data['sex']
    bmi = float(form_data['bmi'])
    children = form_data['children']
    smoker = form_data['smoker']
    region = form_data['region']
    
    if age < 25:
        age_factor = 1.8
    elif age < 30:
        age_factor = 1.5
    elif age < 40:
        age_factor = 1.2
    elif age < 50:
        age_factor = 1.0
    elif age < 65:
        age_factor = 1.1
    else:
        age_factor = 1.4
    
    # Facteur sexe
    sex_factor = 1.1 if sex == 'male' else 1.0
    
    # Facteur BMI
    if bmi < 18.5:
        bmi_factor = 1.2
    elif bmi < 25:
        bmi_factor = 1.0
    elif bmi < 30:
        bmi_factor = 1.1
    elif bmi < 35:
        bmi_factor = 1.3
    else:
        bmi_factor = 1.5
    
    children_factor = 1.0 - (children * 0.05)
    children_factor = max(children_factor, 0.7)
    
    smoker_factor = 2.0 if smoker == 'yes' else 1.0
    
    region_factors = {
        'northwest': 1.0,
        'northeast': 1.1,
        'southwest': 1.05,
        'southeast': 1.15,
    }
    region_factor = region_factors.get(region, 1.0)
    
    premium = base_premium * age_factor * sex_factor * bmi_factor
    premium *= children_factor * smoker_factor * region_factor
    
    return round(premium, 2)
