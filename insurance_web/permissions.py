from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext as _


def check_user_authenticated(user):
    """Vérifie que l'utilisateur est authentifié"""
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        raise PermissionDenied(_("You must be authenticated to access this resource."))


def check_user_permission(user):
    """Vérifie que l'utilisateur a un profil utilisateur valide"""
    check_user_authenticated(user)
    if not hasattr(user, 'profile'):
        raise PermissionDenied(_("User profile not found."))


def check_conseiller_permission(user, allow_admin=True):
    """Vérifie que l'utilisateur est conseiller (ou admin si allow_admin=True)"""
    check_user_permission(user)
    if not user.profile.is_conseiller():
        if not (allow_admin and user.profile.is_admin()):
            raise PermissionDenied(_("You do not have the necessary permissions to access this resource."))


def check_admin_permission(user):
    """Vérifie que l'utilisateur est administrateur"""
    check_user_permission(user)
    if not user.profile.is_admin():
        raise PermissionDenied(_("You do not have administrator permissions to access this resource."))


def check_own_resource_or_admin(user, resource_user):
    """Vérifie que l'utilisateur est propriétaire de la ressource ou est admin"""
    check_user_permission(user)
    if user.id != resource_user.id and not user.profile.is_admin():
        raise PermissionDenied(_("You can only access your own resources."))


def check_not_self_action(user, target_user, action_name="perform this action"):
    """Vérifie qu'un utilisateur n'effectue pas une action sur lui-même"""
    check_user_permission(user)
    if user.id == target_user.id:
        raise PermissionDenied(_("You cannot %(action)s on your own account.") % {'action': action_name})


def has_conseiller_permission(user, allow_admin=True):
    """Retourne True si l'utilisateur est conseiller (ou admin si allow_admin=True)"""
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return False
    if user.profile.is_conseiller():
        return True
    if allow_admin and user.profile.is_admin():
        return True
    return False


def has_admin_permission(user):
    """Retourne True si l'utilisateur est administrateur"""
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return False
    return user.profile.is_admin()
