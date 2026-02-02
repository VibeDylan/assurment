from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    HomeView,
    SignupView,
    LogoutView,
    ProfileView,
    EditProfileView,
    PredictView,
    ConseillersListView,
    ConseillerAvailabilityView,
    CreateAppointmentView,
    MyAppointmentsView,
    ConseillerDashboardView,
    ConseillerPredictView,
    ConseillerCalendarView,
    ConseillerClientsListView,
    AdminDashboardView,
    AdminUserManagementView,
    AdminChangeUserRoleView,
    AdminToggleUserStatusView,
    AdminDeleteUserView,
)

app_name = 'insurance_web'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='authentification/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('conseillers/', ConseillersListView.as_view(), name='conseillers_list'),
    path('conseiller/<int:conseiller_id>/availability/', ConseillerAvailabilityView.as_view(), name='conseiller_availability'),
    path('conseiller/<int:conseiller_id>/book/', CreateAppointmentView.as_view(), name='create_appointment'),
    path('appointments/', MyAppointmentsView.as_view(), name='my_appointments'),
    
    path('conseiller/', ConseillerDashboardView.as_view(), name='conseiller_dashboard'),
    path('conseiller/predict/', ConseillerPredictView.as_view(), name='conseiller_predict'),
    path('conseiller/predict/<int:client_id>/', ConseillerPredictView.as_view(), name='conseiller_predict_client'),
    path('conseiller/calendar/', ConseillerCalendarView.as_view(), name='conseiller_calendar'),
    path('conseiller/clients/', ConseillerClientsListView.as_view(), name='conseiller_clients'),
    
    path('management/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('management/users/', AdminUserManagementView.as_view(), name='admin_user_management'),
    path('management/users/<int:user_id>/change-role/', AdminChangeUserRoleView.as_view(), name='admin_change_user_role'),
    path('management/users/<int:user_id>/toggle-status/', AdminToggleUserStatusView.as_view(), name='admin_toggle_user_status'),
    path('management/users/<int:user_id>/delete/', AdminDeleteUserView.as_view(), name='admin_delete_user'),
]
