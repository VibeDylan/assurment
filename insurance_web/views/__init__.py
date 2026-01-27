from .user_views import (
    home, signup, profile, logout_view, predict,
    conseillers_list, conseiller_availability, create_appointment, my_appointments
)
from . import conseiller_views
from . import admin_views

__all__ = [
    'home', 'signup', 'profile', 'logout_view', 'predict',
    'conseillers_list', 'conseiller_availability', 'create_appointment', 'my_appointments',
    'conseiller_views', 'admin_views'
]
