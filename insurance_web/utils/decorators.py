from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def advice_required(view_func):
    """
    Décorateur pour les vuew réservées aux conseillers.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        if not request.user.profile.is_advice:
            messages.error(request, 'Vous n\'avez pas les permissions requises pour accéder à cette page.')
            return redirect('insurance_web:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def advice_or_admin_required(view_func):
    """Décorateur pour les vues réservées aux conseillers et admins."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        
        if not (request.user.profile.is_advice() or request.user.is_staff):
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('insurance_web:home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view