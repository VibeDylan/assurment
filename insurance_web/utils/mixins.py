
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

class ConseillerRequiredMixin(LoginRequiredMixin):
    """Mixin pour les vues class-based réservées aux conseillers.""" 
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_advice():
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin pour les vues class-based réservées aux admins."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)