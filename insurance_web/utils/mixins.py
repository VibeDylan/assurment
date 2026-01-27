from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class ConseillerRequiredMixin(LoginRequiredMixin):
    """Mixin that checks if the user has the 'conseiller' or 'admin' role.
    Admins have all the same rights as conseillers."""
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.profile.is_conseiller() or request.user.profile.is_admin()):
            messages.error(request, "You do not have the necessary permissions.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin qui vérifie que l'utilisateur a le rôle 'admin' dans l'application.
    Note: Ceci vérifie le rôle admin de l'application (Profile.role='admin'),
    et non les permissions Django admin (is_staff/is_superuser)."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_admin():
            messages.error(request, "You do not have the necessary permissions.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)