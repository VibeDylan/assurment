from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from ..forms import CustomUserCreationForm


class HomeView(TemplateView):
    template_name = 'home.html'


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
