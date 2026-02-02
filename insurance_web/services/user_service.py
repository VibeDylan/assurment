from ..utils.logging import log_error

def update_profile_from_form_data(profile, form_data):
    """Met à jour le profil utilisateur avec les données du formulaire"""
    for key, value in form_data.items():
        try:
            if hasattr(profile, key):
                setattr(profile, key, value)
        except Exception as e:
            log_error(f"Error updating profile from form data: {e}")
            continue
    try:
        profile.save()
    except Exception as e:
        log_error(f"Error saving profile: {e}")
        return None
    return profile


def get_profile_initial_data(profile):
    """Récupère les données initiales du profil pour pré-remplir un formulaire (prédiction ou profil)."""
    initial = {}
    if profile:
        if profile.age is not None:
            initial['age'] = profile.age
        if profile.sex:
            initial['sex'] = profile.sex
        if getattr(profile, 'height', None) is not None:
            initial['height'] = profile.height
        if getattr(profile, 'weight', None) is not None:
            initial['weight'] = profile.weight
        if profile.bmi is not None and 'height' not in initial and 'weight' not in initial:
            initial['bmi'] = profile.bmi
        if profile.children is not None:
            initial['children'] = profile.children
        if profile.smoker:
            initial['smoker'] = profile.smoker
        if profile.region:
            initial['region'] = profile.region
        if profile.additional_info:
            initial['additional_info'] = profile.additional_info
    return initial
