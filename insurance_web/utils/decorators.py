from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def conseiller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        if not request.user.profile.is_conseiller():
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('insurance_web:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def conseiller_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('insurance_web:login')
        if not (request.user.profile.is_conseiller() or request.user.profile.is_admin()):
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('insurance_web:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view