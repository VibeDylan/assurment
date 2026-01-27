from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class ConseillerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_conseiller():
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_admin():
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)