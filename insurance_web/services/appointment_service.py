from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
from calendar import monthrange

from ..models import Appointment
from ..utils.logging import log_error, log_appointment, log_warning
from ..exceptions import AppointmentError, AppointmentConflictError
from .notification_service import (
    create_appointment_request_notification,
    create_appointment_response_notification,
    create_appointment_by_conseiller_notification,
    create_notification,
)


def get_available_slots(conseiller, selected_date, existing_appointments):
    """Calcule les créneaux disponibles pour un conseiller à une date donnée"""
    available_slots = []
    
    if not selected_date:
        return available_slots
    
    try:
        start_datetime = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
        end_datetime = start_datetime + timedelta(days=1)
        
        booked_slots = set()
        for apt in existing_appointments.filter(
            date_time__gte=start_datetime,
            date_time__lt=end_datetime
        ).exclude(status='cancelled'):
            slot_start = apt.date_time.replace(minute=0, second=0, microsecond=0)
            for i in range(apt.duration_minutes // 30):
                booked_slots.add(slot_start + timedelta(minutes=i * 30))
        
        start_hour = 9
        end_hour = 18
        current_slot = start_datetime.replace(hour=start_hour)
        
        while current_slot.hour < end_hour:
            if current_slot not in booked_slots and current_slot > timezone.now():
                available_slots.append(current_slot)
            current_slot += timedelta(minutes=30)
    except ValueError as e:
        log_error(_("Error getting available slots: %(error)s") % {'error': e})
        return available_slots
    
    return available_slots


def check_appointment_conflict(conseiller, date_time, duration_minutes):
    """
    Vérifie s'il y a un conflit avec un rendez-vous existant.
    
    Args:
        conseiller: Conseiller pour qui vérifier le conflit
        date_time: Date et heure du rendez-vous
        duration_minutes: Durée en minutes
        
    Returns:
        tuple: (has_conflict: bool, error_message: str | None)
        
    Raises:
        AppointmentConflictError: Si le créneau est dans le passé
    """
    if date_time <= timezone.now():
        raise AppointmentConflictError(_("You cannot book a time slot in the past."))
    
    conflicting_appointments = Appointment.objects.filter(
        conseiller=conseiller,
        date_time__lt=date_time + timedelta(minutes=duration_minutes),
        date_time__gte=date_time - timedelta(minutes=duration_minutes)
    ).exclude(status='cancelled')
    
    if conflicting_appointments.exists():
        return True, _("This time slot is no longer available. Please choose another one.")
    
    return False, None


@transaction.atomic
def create_appointment(conseiller, client, date_time, duration_minutes, notes='', created_by_conseiller=False):
    """
    Crée un nouveau rendez-vous.
    
    Args:
        conseiller: Conseiller pour le rendez-vous
        client: Client du rendez-vous
        date_time: Date et heure du rendez-vous
        duration_minutes: Durée en minutes
        notes: Notes optionnelles
        created_by_conseiller: Si True, le conseiller a créé le RDV (on notifie le client) ; sinon le client a réservé (on notifie le conseiller)
        
    Returns:
        Appointment: Instance de rendez-vous créée
        
    Raises:
        AppointmentError: Si une erreur survient lors de la création
    """
    try:
        appointment = Appointment.objects.create(
            conseiller=conseiller,
            client=client,
            date_time=date_time,
            duration_minutes=duration_minutes,
            notes=notes
        )
        log_appointment(appointment, 'created')
    
        try:
            if created_by_conseiller:
                create_appointment_by_conseiller_notification(appointment)
            else:
                create_appointment_request_notification(appointment)
        except Exception as notification_error:
            log_warning(
                _("Failed to create notification for appointment: %(error)s") % {'error': notification_error},
                extra={
                    'appointment_id': appointment.id,
                    'conseiller_id': conseiller.id,
                }
            )
        return appointment
    except Exception as e:
        log_error(
            _("Error creating appointment: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'conseiller_id': conseiller.id,
                'client_id': client.id,
                'date_time': date_time.isoformat(),
            }
        )
        raise AppointmentError(_("Failed to create appointment: %(error)s") % {'error': e})


def get_appointments_for_calendar(conseiller, year=None, month=None):
    """Récupère les rendez-vous pour un calendrier mensuel"""
    if year and month:
        try:
            current_date = datetime(int(year), int(month), 1).date()
        except (ValueError, TypeError) as e:
            log_error(f"Invalid date parameters: year={year}, month={month}", exc_info=True)
            current_date = datetime.now().date().replace(day=1)
    else:
        current_date = datetime.now().date().replace(day=1)
    
    first_day = current_date.replace(day=1)
    last_day_num = monthrange(current_date.year, current_date.month)[1]
    last_day = current_date.replace(day=last_day_num)
    
    if conseiller.profile.is_admin():
        appointments = Appointment.objects.filter(
            date_time__date__gte=first_day,
            date_time__date__lte=last_day
        ).exclude(status='cancelled').order_by('date_time')
    else:
        appointments = Appointment.objects.filter(
            conseiller=conseiller,
            date_time__date__gte=first_day,
            date_time__date__lte=last_day
        ).exclude(status='cancelled').order_by('date_time')
    
    appointments_by_date = {}
    for appointment in appointments:
        day = appointment.date_time.date()
        if day not in appointments_by_date:
            appointments_by_date[day] = []
        appointments_by_date[day].append(appointment)
    
    return appointments_by_date, current_date, first_day, last_day_num, last_day


@transaction.atomic
def accept_appointment(appointment_id, conseiller):
    """
    Accepte un rendez-vous en attente.
    
    Args:
        appointment_id: ID du rendez-vous à accepter
        conseiller: Conseiller qui accepte (pour vérification de sécurité)
        
    Returns:
        Appointment: Instance de rendez-vous mise à jour
        
    Raises:
        AppointmentError: Si le rendez-vous n'existe pas, n'est pas en attente, 
                         ou n'appartient pas au conseiller
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        if appointment.conseiller != conseiller:
            raise AppointmentError(_("You can only accept appointments assigned to you."))
        
        if appointment.status != 'pending':
            raise AppointmentError(_("This appointment is not pending and cannot be accepted."))
        
        appointment.status = 'confirmed'
        appointment.save()
        
        log_appointment(appointment, 'accepted')
        
        try:
            create_appointment_response_notification(appointment, 'accepted')
        except Exception as notification_error:
            log_warning(
                _("Failed to create notification for appointment acceptance: %(error)s") % {'error': notification_error},
                extra={
                    'appointment_id': appointment.id,
                    'conseiller_id': conseiller.id,
                }
            )
        
        return appointment
    except Appointment.DoesNotExist:
        raise AppointmentError(_("Appointment not found."))
    except AppointmentError:
        raise
    except Exception as e:
        log_error(
            _("Error accepting appointment: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'appointment_id': appointment_id,
                'conseiller_id': conseiller.id,
            }
        )
        raise AppointmentError(_("Failed to accept appointment: %(error)s") % {'error': e})


@transaction.atomic
def reject_appointment(appointment_id, conseiller, reason=None):
    """
    Refuse un rendez-vous en attente.
    
    Args:
        appointment_id: ID du rendez-vous à refuser
        conseiller: Conseiller qui refuse (pour vérification de sécurité)
        reason: Raison du refus (optionnel)
        
    Returns:
        Appointment: Instance de rendez-vous mise à jour
        
    Raises:
        AppointmentError: Si le rendez-vous n'existe pas, n'est pas en attente, 
                         ou n'appartient pas au conseiller
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Vérifications de sécurité
        if appointment.conseiller != conseiller:
            raise AppointmentError(_("You can only reject appointments assigned to you."))
        
        if appointment.status != 'pending':
            raise AppointmentError(_("This appointment is not pending and cannot be rejected."))
        
        # Mettre à jour le statut
        appointment.status = 'cancelled'
        appointment.save()
        
        log_appointment(appointment, 'rejected')
        
        # Créer la notification pour le client
        try:
            create_appointment_response_notification(appointment, 'rejected', reason=reason)
        except Exception as notification_error:
            log_warning(
                _("Failed to create notification for appointment rejection: %(error)s") % {'error': notification_error},
                extra={
                    'appointment_id': appointment.id,
                    'conseiller_id': conseiller.id,
                }
            )
        
        return appointment
    except Appointment.DoesNotExist:
        raise AppointmentError(_("Appointment not found."))
    except AppointmentError:
        raise
    except Exception as e:
        log_error(
            _("Error rejecting appointment: %(error)s") % {'error': e},
            exc_info=True,
            extra={
                'appointment_id': appointment_id,
                'conseiller_id': conseiller.id,
            }
        )
        raise AppointmentError(_("Failed to reject appointment: %(error)s") % {'error': e})


def cancel_appointment(appointment_id, user):
    """
    Annule un rendez-vous (client, conseiller ou admin).
    Le rendez-vous doit être en attente ou confirmé.
    
    Args:
        appointment_id: ID du rendez-vous
        user: Utilisateur qui annule (client, conseiller du rendez-vous, ou admin)
        
    Returns:
        Appointment: Rendez-vous annulé
        
    Raises:
        AppointmentError: Si le rendez-vous n'existe pas, n'est pas annulable, ou si l'utilisateur n'a pas le droit
    """
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
        
        is_admin = hasattr(user, 'profile') and user.profile.is_admin()
        if user != appointment.client and user != appointment.conseiller and not is_admin:
            raise AppointmentError(_("You can only cancel your own appointments."))
        
        if appointment.status == 'cancelled':
            raise AppointmentError(_("This appointment is already cancelled."))
        
        appointment.status = 'cancelled'
        appointment.save()
        
        log_appointment(appointment, 'cancelled')
        
        other_user = appointment.client if user == appointment.conseiller else appointment.conseiller
        canceller_name = user.get_full_name() or user.email
        appointment_date = appointment.date_time.strftime('%d/%m/%Y à %H:%M')
        message = _("The appointment with %(canceller)s on %(date)s has been cancelled.") % {
            'canceller': canceller_name,
            'date': appointment_date,
        }
        try:
            create_notification(
                user=other_user,
                notification_type='appointment_cancelled',
                message=message,
                appointment=appointment,
            )
        except Exception as notification_error:
            log_warning(
                _("Failed to create cancellation notification: %(error)s") % {'error': notification_error},
                extra={'appointment_id': appointment.id},
            )
        
        return appointment
    except Appointment.DoesNotExist:
        raise AppointmentError(_("Appointment not found."))
    except AppointmentError:
        raise
    except Exception as e:
        log_error(
            _("Error cancelling appointment: %(error)s") % {'error': e},
            exc_info=True,
            extra={'appointment_id': appointment_id, 'user_id': user.id},
        )
        raise AppointmentError(_("Failed to cancel appointment: %(error)s") % {'error': e})


def reschedule_appointment(appointment_id, user, new_date_time, duration_minutes=None, notes=None):
    """
    Reporte un rendez-vous à une nouvelle date/heure (client, conseiller ou admin).
    Le rendez-vous doit être en attente ou confirmé.
    
    Args:
        appointment_id: ID du rendez-vous
        user: Utilisateur qui reporte (client, conseiller du rendez-vous, ou admin)
        new_date_time: Nouvelle date et heure (timezone-aware)
        duration_minutes: Nouvelle durée en minutes (optionnel, garde l'actuelle si None)
        notes: Nouvelles notes (optionnel, garde les actuelles si None)
        
    Returns:
        Appointment: Rendez-vous mis à jour
        
    Raises:
        AppointmentError: Si le rendez-vous n'existe pas, n'est pas reportable, ou conflit de créneau
    """
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
        
        is_admin = hasattr(user, 'profile') and user.profile.is_admin()
        if user != appointment.client and user != appointment.conseiller and not is_admin:
            raise AppointmentError(_("You can only reschedule your own appointments."))
        
        if appointment.status == 'cancelled':
            raise AppointmentError(_("Cannot reschedule a cancelled appointment."))
        
        if new_date_time <= timezone.now():
            raise AppointmentConflictError(_("You cannot reschedule to a past date or time."))
        
        duration = duration_minutes if duration_minutes is not None else appointment.duration_minutes
        new_end = new_date_time + timedelta(minutes=duration)
        
        # Vérifier les conflits en excluant ce rendez-vous (chevauchement de créneaux)
        other_appointments = Appointment.objects.filter(
            conseiller=appointment.conseiller,
        ).exclude(status='cancelled').exclude(pk=appointment_id)
        
        for other in other_appointments:
            other_end = other.date_time + timedelta(minutes=other.duration_minutes)
            if other.date_time < new_end and other_end > new_date_time:
                raise AppointmentConflictError(_("This time slot is no longer available. Please choose another one."))
        
        old_date_time = appointment.date_time
        appointment.date_time = new_date_time
        appointment.duration_minutes = duration
        if notes is not None:
            appointment.notes = notes
        appointment.save()
        
        log_appointment(appointment, 'rescheduled')
        
        # Notifier l'autre partie
        other_user = appointment.client if user == appointment.conseiller else appointment.conseiller
        rescheduler_name = user.get_full_name() or user.email
        new_date_str = new_date_time.strftime('%d/%m/%Y à %H:%M')
        message = _("The appointment with %(name)s has been rescheduled to %(date)s.") % {
            'name': rescheduler_name,
            'date': new_date_str,
        }
        try:
            create_notification(
                user=other_user,
                notification_type='appointment_rescheduled',
                message=message,
                appointment=appointment,
            )
        except Exception as notification_error:
            log_warning(
                _("Failed to create reschedule notification: %(error)s") % {'error': notification_error},
                extra={'appointment_id': appointment.id},
            )
        
        return appointment
    except Appointment.DoesNotExist:
        raise AppointmentError(_("Appointment not found."))
    except (AppointmentError, AppointmentConflictError):
        raise
    except Exception as e:
        log_error(
            _("Error rescheduling appointment: %(error)s") % {'error': e},
            exc_info=True,
            extra={'appointment_id': appointment_id, 'user_id': user.id},
        )
        raise AppointmentError(_("Failed to reschedule appointment: %(error)s") % {'error': e})
