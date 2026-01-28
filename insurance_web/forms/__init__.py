from .auth_forms import CustomUserCreationForm
from .prediction_forms import PredictionForm
from .appointment_forms import AppointmentForm
from .admin_forms import AdminUserManagementForm, AdminUserRoleForm

__all__ = [
    'CustomUserCreationForm',
    'PredictionForm',
    'AppointmentForm',
    'AdminUserManagementForm',
    'AdminUserRoleForm',
]
