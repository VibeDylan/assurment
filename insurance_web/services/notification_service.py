from django.utils.translation import gettext as _
from django.utils.formats import date_format
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Notification, Appointment
from ..utils.logging import log_error, log_info
from ..constants import NOTIFICATION_TYPE_CHOICES
from ..exceptions import NotificationError


def create_notification(user, notification_type, message, appointment=None):
    """
    Crée une notification pour un utilisateur.
    
    Args:
        user: Utilisateur pour qui la notification est créée
        notification_type: Type de notification (doit être dans NOTIFICATION_TYPE_CHOICES)
        message: Message de la notification (obligatoire)
        appointment: Rendez-vous associé à la notification (optionnel)
        
    Returns:
        Notification: Instance de notification créée
        
    Raises:
        ValidationError: Si le type de notification est invalide ou si le message est vide
    """
    valid_types = [choice[0] for choice in NOTIFICATION_TYPE_CHOICES]
    if notification_type not in valid_types:
        raise ValidationError(_("Invalid notification type: %(type)s") % {'type': notification_type})
    
    if not message or not message.strip():
        raise ValidationError(_("Notification message cannot be empty"))
    
    try:
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            appointment=appointment,
            message=message
        )
        log_info(
            _("Notification created"),
            extra={
                'notification_id': notification.id,
                'user_id': user.id,
                'notification_type': notification_type,
                'appointment_id': appointment.id if appointment else None,
            }
        )
        return notification
    except Exception as e:
        log_error(
            _("Error creating notification: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'user_id': user.id,
                'notification_type': notification_type,
                'appointment_id': appointment.id if appointment else None,
            }
        )
        raise

def create_appointment_request_notification(appointment):
    """
    Crée une notification pour le conseiller lorsqu'un client demande un rendez-vous.
    
    Args:
        appointment: Instance Appointment créée
        
    Returns:
        Notification: Instance de notification créée
    """
    try:
        conseiller = appointment.conseiller
        appointment_date = appointment.date_time.strftime('%d/%m/%Y à %H:%M')
        message = _("Nouvelle demande de rendez-vous de %(client)s pour %(appointment)s") % {
            'client': appointment.client.get_full_name() or appointment.client.email,
            'appointment': appointment_date
        }
        return create_notification(
            user=conseiller,
            notification_type='appointment_request',
            message=message,
            appointment=appointment
        )
    except Exception as e:
        log_error(
            _("Error creating appointment request notification: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'appointment_id': appointment.id,
            }
        )
        raise NotificationError(_("Failed to create appointment request notification: %(error)s") % {'error': e})


def create_appointment_response_notification(appointment, action, reason=None):
    """
    Crée une notification pour le client lorsqu'un conseiller accepte ou refuse un rendez-vous.
    
    Args:
        appointment: Instance Appointment concernée
        action: 'accepted' ou 'rejected'
        reason: Raison du refus (optionnel, seulement si action='rejected')
        
    Returns:
        Notification: Instance de notification créée
        
    Raises:
        ValidationError: Si l'action n'est pas valide
    """
    valid_actions = ['accepted', 'rejected']
    if action not in valid_actions:
        raise ValidationError(_("Invalid action: %(action)s") % {'action': action})
    
    client = appointment.client
    conseiller_name = appointment.conseiller.get_full_name() or appointment.conseiller.email
    appointment_date = appointment.date_time.strftime('%d/%m/%Y à %H:%M')
    notification_type = 'appointment_accepted' if action == 'accepted' else 'appointment_rejected'
    
    if action == 'accepted':
        message = _("Your appointment with %(conseiller)s on %(date)s has been confirmed.") % {
            'conseiller': conseiller_name,
            'date': appointment_date
        }
    else:
        message = _("Your appointment request with %(conseiller)s on %(date)s has been rejected.") % {
            'conseiller': conseiller_name,
            'date': appointment_date
        }
        if reason:
            message += " " + _("Reason: %(reason)s") % {'reason': reason}
    try:
        return create_notification(
            user=client,
            notification_type=notification_type,
            message=message,
            appointment=appointment
        )
    except Exception as e:
        log_error(
            _("Error creating appointment response notification: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'appointment_id': appointment.id,
                'action': action,
                'reason': reason if reason else '',
                'client_id': client.id,
                'notification_type': notification_type,
            }
        )
        raise NotificationError(_("Failed to create appointment response notification: %(error)s") % {'error': e})


def get_unread_notifications_count(user):
    """
    Retourne le nombre de notifications non lues pour un utilisateur.
    
    Args:
        user: Utilisateur pour qui compter les notifications
        
    Returns:
        int: Nombre de notifications non lues
    """
    return Notification.objects.filter(user=user, read=False).count()


def get_user_notifications(user, unread_only=False, limit=None):
    """
    Récupère les notifications d'un utilisateur.
    
    Args:
        user: Utilisateur pour lequel les notifications sont récupérées
        unread_only: Si True, récupère uniquement les notifications non lues
        limit: Nombre maximum de notifications à récupérer (optionnel)
        
    Returns:
        QuerySet ou list: QuerySet de Notification (ou liste si limit est utilisé)
    """
    try:
        query = Notification.objects.filter(user=user)
        if unread_only:
            query = query.filter(read=False)
        query = query.order_by('-created_at')
        if limit:
            return list(query[:limit])
        return query
    except Exception as e:
        log_error(
            _("Error getting user notifications: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'user_id': user.id,
                'unread_only': unread_only,
                'limit': limit,
            }
        )
        raise NotificationError(_("Failed to get user notifications: %(error)s") % {'error': e})


def mark_notification_as_read(notification_id, user):
    """
    Marque une notification comme lue.
    
    Args:
        notification_id: ID de la notification
        user: Utilisateur propriétaire de la notification (pour sécurité)
        
    Returns:
        bool: True si la notification a été marquée comme lue, False sinon
        
    Raises:
        NotificationError: Si la notification n'existe pas ou n'appartient pas à l'utilisateur
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        if notification.read:
            return False
        notification.read = True
        notification.save()
        log_info(
            _("Notification marked as read"),
            extra={
                'notification_id': notification.id,
                'user_id': user.id,
            }
        )
        return True
    except Notification.DoesNotExist:
        raise NotificationError(_("Notification not found or you don't have permission to access it"))
    except Exception as e:
        log_error(
            _("Error marking notification as read: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'notification_id': notification_id,
                'user_id': user.id,
            }
        )
        raise NotificationError(_("Failed to mark notification as read: %(error)s") % {'error': e})


def mark_all_notifications_as_read(user):
    """
    Marque toutes les notifications d'un utilisateur comme lues.
    
    Args:
        user: Utilisateur pour qui marquer toutes les notifications comme lues
        
    Returns:
        int: Nombre de notifications marquées comme lues
    """
    try:
        count = Notification.objects.filter(user=user, read=False).update(read=True)
        log_info(
            _("All notifications marked as read"),
            extra={
                'user_id': user.id,
                'count': count,
            }
        )
        return count
    except Exception as e:
        log_error(
            _("Error marking all notifications as read: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'user_id': user.id,
            }
        )
        raise NotificationError(_("Failed to mark all notifications as read: %(error)s") % {'error': e})