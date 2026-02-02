from .base import HomeView, SignupView, LogoutView
from .user_views import (
    ProfileView,
    EditProfileView,
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
    ConseillerClientsListView,
    NotificationListView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    AcceptAppointmentView,
    RejectAppointmentView,
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
    'EditProfileView',
    'PredictView',
    'ConseillersListView',
    'ConseillerAvailabilityView',
    'CreateAppointmentView',
    'MyAppointmentsView',
    'ConseillerDashboardView',
    'ConseillerPredictView',
    'ConseillerCalendarView',
    'ConseillerClientsListView',
    'NotificationListView',
    'MarkNotificationReadView',
    'MarkAllNotificationsReadView',
    'AcceptAppointmentView',
    'RejectAppointmentView',
    'AdminDashboardView',
    'AdminUserManagementView',
    'AdminChangeUserRoleView',
    'AdminToggleUserStatusView',
    'AdminDeleteUserView',
]
