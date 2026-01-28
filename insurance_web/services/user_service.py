from ..models import Profile


def update_profile_from_form_data(profile, form_data):
    """Met à jour le profil utilisateur avec les données du formulaire"""
    for key, value in form_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    profile.save()
    return profile


def get_profile_initial_data(profile):
    """Récupère les données initiales du profil pour pré-remplir un formulaire"""
    initial = {}
    if profile:
        if profile.age is not None:
            initial['age'] = profile.age
        if profile.sex:
            initial['sex'] = profile.sex
        if profile.bmi is not None:
            initial['bmi'] = profile.bmi
        if profile.children is not None:
            initial['children'] = profile.children
        if profile.smoker:
            initial['smoker'] = profile.smoker
        if profile.region:
            initial['region'] = profile.region
    return initial
