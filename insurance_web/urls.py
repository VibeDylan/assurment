from django.urls import path
from django.contrib.auth import views as auth_views
from .views import cbv_views

app_name = 'insurance_web'

urlpatterns = [
    # Vues publiques
    path('', cbv_views.HomeView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='authentification/login.html'), name='login'),
    path('logout/', cbv_views.LogoutView.as_view(), name='logout'),
    path('signup/', cbv_views.SignupView.as_view(), name='signup'),
    
    # Vues utilisateur authentifié
    path('profile/', cbv_views.ProfileView.as_view(), name='profile'),
    path('predict/', cbv_views.PredictView.as_view(), name='predict'),
    path('conseillers/', cbv_views.ConseillersListView.as_view(), name='conseillers_list'),
    path('conseiller/<int:conseiller_id>/availability/', cbv_views.ConseillerAvailabilityView.as_view(), name='conseiller_availability'),
    path('conseiller/<int:conseiller_id>/book/', cbv_views.CreateAppointmentView.as_view(), name='create_appointment'),
    path('appointments/', cbv_views.MyAppointmentsView.as_view(), name='my_appointments'),
    
    # Vues conseiller
    path('conseiller/', cbv_views.ConseillerDashboardView.as_view(), name='conseiller_dashboard'),
    path('conseiller/predict/', cbv_views.ConseillerPredictView.as_view(), name='conseiller_predict'),
    path('conseiller/predict/<int:client_id>/', cbv_views.ConseillerPredictView.as_view(), name='conseiller_predict_client'),
    path('conseiller/calendar/', cbv_views.ConseillerCalendarView.as_view(), name='conseiller_calendar'),
    path('conseiller/clients/', cbv_views.ConseillerClientsListView.as_view(), name='conseiller_clients'),
    
    # Vues admin
    path('management/', cbv_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('management/users/', cbv_views.AdminUserManagementView.as_view(), name='admin_user_management'),
    path('management/users/<int:user_id>/change-role/', cbv_views.AdminChangeUserRoleView.as_view(), name='admin_change_user_role'),
    path('management/users/<int:user_id>/toggle-status/', cbv_views.AdminToggleUserStatusView.as_view(), name='admin_toggle_user_status'),
    path('management/users/<int:user_id>/delete/', cbv_views.AdminDeleteUserView.as_view(), name='admin_delete_user'),
]
