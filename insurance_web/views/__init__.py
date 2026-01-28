from .base import HomeView, SignupView, LogoutView
from .user_views import (
    ProfileView,
    PredictView,
    ConseillersListView,
    ConseillerAvailabilityView,
    CreateAppointmentView,
    MyAppointmentsView
)
from .conseiller_views import (
    ConseillerDashboardView,
    ConseillerPredictView,
    ConseillerCalendarView,
    ConseillerClientsListView
)
from .admin_views import (
    AdminDashboardView,
    AdminUserManagementView,
    AdminChangeUserRoleView,
    AdminToggleUserStatusView,
    AdminDeleteUserView
)

__all__ = [
    'HomeView',
    'SignupView',
    'LogoutView',
    'ProfileView',
    'PredictView',
    'ConseillersListView',
    'ConseillerAvailabilityView',
    'CreateAppointmentView',
    'MyAppointmentsView',
    'ConseillerDashboardView',
    'ConseillerPredictView',
    'ConseillerCalendarView',
    'ConseillerClientsListView',
    'AdminDashboardView',
    'AdminUserManagementView',
    'AdminChangeUserRoleView',
    'AdminToggleUserStatusView',
    'AdminDeleteUserView',
]
