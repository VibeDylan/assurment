from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import conseiller_views, admin_views

app_name = 'insurance_web'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='authentification/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('predict/', views.predict, name='predict'),
    path('conseillers/', views.conseillers_list, name='conseillers_list'),
    path('conseiller/<int:conseiller_id>/availability/', views.conseiller_availability, name='conseiller_availability'),
    path('conseiller/<int:conseiller_id>/book/', views.create_appointment, name='create_appointment'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('conseiller/', conseiller_views.conseiller_dashboard, name='conseiller_dashboard'),
    path('conseiller/predict/', conseiller_views.conseiller_predict_for_client, name='conseiller_predict'),
    path('conseiller/predict/<int:client_id>/', conseiller_views.conseiller_predict_for_client, name='conseiller_predict_client'),
    path('conseiller/calendar/', conseiller_views.conseiller_calendar, name='conseiller_calendar'),
    path('conseiller/clients/', conseiller_views.conseiller_clients_list, name='conseiller_clients'),
    path('management/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('management/users/', admin_views.admin_user_management, name='admin_user_management'),
    path('management/users/<int:user_id>/change-role/', admin_views.admin_change_user_role, name='admin_change_user_role'),
    path('management/users/<int:user_id>/toggle-status/', admin_views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('management/users/<int:user_id>/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
]
