from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from ..permissions import check_conseiller_permission, check_admin_permission


class ConseillerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        try:
            check_conseiller_permission(request.user, allow_admin=True)
        except PermissionDenied:
            messages.error(request, "You do not have the necessary permissions to access this page.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        try:
            check_admin_permission(request.user)
        except PermissionDenied:
            messages.error(request, "You do not have the necessary permissions to access this page.")
            return redirect('insurance_web:home')
        return super().dispatch(request, *args, **kwargs)


class UserProfileMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_profile'] = self.request.user.profile
        return context