from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def conseiller_required(view_func):
    """Decorator that checks if the user has the 'conseiller' or 'admin' role.
    Admins have all the same rights as conseillers."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        if not (request.user.profile.is_conseiller() or request.user.profile.is_admin()):
            messages.error(request, "You do not have the necessary permissions to access this page.")
            return redirect('insurance_web:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """Décorateur qui vérifie que l'utilisateur a le rôle 'admin' dans l'application.
    Note: Ceci vérifie le rôle admin de l'application (Profile.role='admin'),
    et non les permissions Django admin (is_staff/is_superuser)."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        if not request.user.profile.is_admin():
            messages.error(request, "You do not have the necessary permissions to access this page.")
            return redirect('insurance_web:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def conseiller_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        if not (request.user.profile.is_conseiller() or request.user.profile.is_admin()):
            messages.error(request, "You do not have the necessary permissions.")
            return redirect('insurance_web:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view