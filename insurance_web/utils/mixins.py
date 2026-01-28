from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class ConseillerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.profile.is_conseiller() or request.user.profile.is_admin()):
            messages.error(request, "You do not have the necessary permissions.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_admin():
            messages.error(request, "You do not have the necessary permissions.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)