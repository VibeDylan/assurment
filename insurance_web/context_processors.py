from .services.notification_service import get_unread_notifications_count


def notifications(request):
    """Ajoute le nombre de notifications non lues au contexte de tous les templates"""
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': get_unread_notifications_count(request.user)
        }
    return {
        'unread_notifications_count': 0
    }
