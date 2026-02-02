from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _

from ..forms import CustomUserCreationForm
from ..models import Appointment, Prediction
from ..services.notification_service import get_unread_notifications_count


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_template_names(self):
        """Retourne le template approprié selon le rôle de l'utilisateur"""
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            if profile.is_admin():
                return ['admin/dashboard.html']
            elif profile.is_conseiller():
                return ['conseiller/dashboard.html']
            else:
                return ['client/dashboard.html']
        return ['home.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            user = self.request.user
            profile = user.profile
            
            if profile.is_admin():
                # Contexte pour le tableau de bord admin
                from ..models import User
                context.update({
                    'total_users': User.objects.count(),
                    'total_conseillers': User.objects.filter(profile__role='conseiller').count(),
                    'total_appointments': Appointment.objects.exclude(status='cancelled').count(),
                    'total_predictions': Prediction.objects.count(),
                })
                # Ajouter le formulaire pour créer un utilisateur
                from ..forms import AdminUserManagementForm
                context['form'] = AdminUserManagementForm()
                
            elif profile.is_conseiller():
                # Contexte pour le tableau de bord conseiller
                conseiller = user
                
                if conseiller.profile.is_admin():
                    total_appointments = Appointment.objects.exclude(status='cancelled').count()
                    upcoming_appointments = Appointment.objects.filter(
                        date_time__gte=timezone.now()
                    ).exclude(status='cancelled').count()
                    next_appointments = Appointment.objects.filter(
                        date_time__gte=timezone.now()
                    ).exclude(status='cancelled').order_by('date_time')[:5]
                    pending_appointments = Appointment.objects.filter(
                        status='pending',
                        date_time__gte=timezone.now()
                    ).order_by('date_time')[:10]
                else:
                    total_appointments = Appointment.objects.filter(conseiller=conseiller).exclude(status='cancelled').count()
                    upcoming_appointments = Appointment.objects.filter(
                        conseiller=conseiller,
                        date_time__gte=timezone.now()
                    ).exclude(status='cancelled').count()
                    next_appointments = Appointment.objects.filter(
                        conseiller=conseiller,
                        date_time__gte=timezone.now()
                    ).exclude(status='cancelled').order_by('date_time')[:5]
                    pending_appointments = Appointment.objects.filter(
                        conseiller=conseiller,
                        status='pending',
                        date_time__gte=timezone.now()
                    ).order_by('date_time')[:10]
                
                unread_notifications_count = get_unread_notifications_count(conseiller)
                
                context.update({
                    'total_appointments': total_appointments,
                    'upcoming_appointments': upcoming_appointments,
                    'next_appointments': next_appointments,
                    'pending_appointments': pending_appointments,
                    'unread_notifications_count': unread_notifications_count,
                })
                
            else:
                # Contexte pour le tableau de bord client
                client = user
                
                # Statistiques des rendez-vous
                total_appointments = Appointment.objects.filter(client=client).exclude(status='cancelled').count()
                upcoming_appointments = Appointment.objects.filter(
                    client=client,
                    date_time__gte=timezone.now()
                ).exclude(status='cancelled').order_by('date_time')[:5]
                
                # Statistiques des prédictions
                total_predictions = Prediction.objects.filter(user=client).count()
                latest_prediction = Prediction.objects.filter(user=client).order_by('-created_at').first()
                
                # Notifications non lues
                unread_notifications_count = get_unread_notifications_count(client)
                
                context.update({
                    'total_appointments': total_appointments,
                    'upcoming_appointments': upcoming_appointments,
                    'total_predictions': total_predictions,
                    'latest_prediction': latest_prediction,
                    'unread_notifications_count': unread_notifications_count,
                })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Gère la création d'utilisateur pour les admins"""
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_admin():
            from ..forms import AdminUserManagementForm
            form = AdminUserManagementForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(
                    request,
                    _('User %(name)s created successfully with role %(role)s.') % {
                        'name': user.get_full_name() or user.email,
                        'role': user.profile.get_role_display()
                    }
                )
                return self.get(request, *args, **kwargs)
            else:
                context = self.get_context_data(**kwargs)
                context['form'] = form
                return self.render_to_response(context)
        return self.get(request, *args, **kwargs)


class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'authentification/signup.html'
    success_url = reverse_lazy('insurance_web:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, _('Welcome %(name)s!') % {'name': self.object.get_full_name() or self.object.email})
        return response


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('insurance_web:home')
