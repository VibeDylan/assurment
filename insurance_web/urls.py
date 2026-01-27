"""
URL configuration for insurance_web app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'insurance_web'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='authentification/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('predict/', views.predict, name='predict'),
]
