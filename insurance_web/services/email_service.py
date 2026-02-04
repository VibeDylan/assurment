"""
Service d'envoi d'emails pour les notifications de rendez-vous.
"""
import os
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _, activate, get_language
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from ..utils.logging import log_error, log_info, log_warning


def send_appointment_confirmation_email(appointment, recipient=None):
    """
    Envoie un email de confirmation de rendez-vous.
    
    Args:
        appointment: Instance Appointment
        recipient: Utilisateur destinataire (par défaut: le client)
        
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    if recipient is None:
        recipient = appointment.client
    
    if not recipient.email:
        log_warning(
            _("Cannot send email: recipient %(user)s has no email address") % {'user': recipient.username},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False
    
    try:
        user_language = getattr(recipient, 'profile', None)
        if user_language and hasattr(user_language, 'language'):
            lang_code = user_language.language
            if lang_code and '-' in lang_code:
                lang_code = lang_code.split('-')[0]
            activate(lang_code)
        else:
            activate('fr')
        
        site_url = os.getenv('SITE_URL', 'http://localhost:8000')
        lang_code = get_language() or 'fr'
        appointment_url = f"{site_url}/{lang_code}{reverse('insurance_web:appointment_detail', args=[appointment.id])}"
        
        context = {
            'appointment': appointment,
            'recipient': recipient,
            'conseiller': appointment.conseiller,
            'client': appointment.client,
            'appointment_date': appointment.date_time.strftime('%d/%m/%Y'),
            'appointment_time': appointment.date_time.strftime('%H:%M'),
            'site_url': site_url,
            'appointment_url': appointment_url,
        }
        
        html_content = render_to_string('emails/appointment_confirmation.html', context)
        text_content = render_to_string('emails/appointment_confirmation.txt', context)
        
        subject = _("Confirmation de votre rendez-vous - %(date)s") % {'date': context['appointment_date']}
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        email.send()
        
        log_info(
            _("Appointment confirmation email sent to %(email)s") % {'email': recipient.email},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return True
        
    except Exception as e:
        log_error(
            _("Error sending appointment confirmation email: %(error)s") % {'error': e},
            exc_info=True,
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False


def send_appointment_cancellation_email(appointment, cancelled_by, recipient=None):
    """
    Envoie un email d'annulation de rendez-vous.
    
    Args:
        appointment: Instance Appointment annulé
        cancelled_by: Utilisateur qui a annulé le rendez-vous
        recipient: Utilisateur destinataire (par défaut: l'autre partie)
        
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    if recipient is None:
        recipient = appointment.conseiller if cancelled_by == appointment.client else appointment.client
    
    if not recipient.email:
        log_warning(
            _("Cannot send email: recipient %(user)s has no email address") % {'user': recipient.username},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False
    
    try:
        user_language = getattr(recipient, 'profile', None)
        if user_language and hasattr(user_language, 'language'):
            lang_code = user_language.language
            if lang_code and '-' in lang_code:
                lang_code = lang_code.split('-')[0]
            activate(lang_code)
        else:
            activate('fr')
        
        site_url = os.getenv('SITE_URL', 'http://localhost:8000')
        lang_code = get_language() or 'fr'
        appointment_url = f"{site_url}/{lang_code}{reverse('insurance_web:appointment_detail', args=[appointment.id])}"
        
        context = {
            'appointment': appointment,
            'recipient': recipient,
            'cancelled_by': cancelled_by,
            'cancelled_by_name': cancelled_by.get_full_name() or cancelled_by.email,
            'appointment_date': appointment.date_time.strftime('%d/%m/%Y'),
            'appointment_time': appointment.date_time.strftime('%H:%M'),
            'site_url': site_url,
            'appointment_url': appointment_url,
        }
        
        html_content = render_to_string('emails/appointment_cancellation.html', context)
        text_content = render_to_string('emails/appointment_cancellation.txt', context)
        
        subject = _("Annulation de rendez-vous - %(date)s") % {'date': context['appointment_date']}
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        email.send()
        
        log_info(
            _("Appointment cancellation email sent to %(email)s") % {'email': recipient.email},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return True
        
    except Exception as e:
        log_error(
            _("Error sending appointment cancellation email: %(error)s") % {'error': e},
            exc_info=True,
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False


def send_appointment_rescheduled_email(appointment, rescheduled_by, old_date_time, recipient=None):
    """
    Envoie un email de report de rendez-vous.
    
    Args:
        appointment: Instance Appointment reporté
        rescheduled_by: Utilisateur qui a reporté le rendez-vous
        old_date_time: Ancienne date et heure du rendez-vous
        recipient: Utilisateur destinataire (par défaut: l'autre partie)
        
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    if recipient is None:
        recipient = appointment.conseiller if rescheduled_by == appointment.client else appointment.client
    
    if not recipient.email:
        log_warning(
            _("Cannot send email: recipient %(user)s has no email address") % {'user': recipient.username},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False
    
    try:
        user_language = getattr(recipient, 'profile', None)
        if user_language and hasattr(user_language, 'language'):
            lang_code = user_language.language
            if lang_code and '-' in lang_code:
                lang_code = lang_code.split('-')[0]
            activate(lang_code)
        else:
            activate('fr')
        
        site_url = os.getenv('SITE_URL', 'http://localhost:8000')
        lang_code = get_language() or 'fr'
        appointment_url = f"{site_url}/{lang_code}{reverse('insurance_web:appointment_detail', args=[appointment.id])}"
        
        context = {
            'appointment': appointment,
            'recipient': recipient,
            'rescheduled_by': rescheduled_by,
            'rescheduled_by_name': rescheduled_by.get_full_name() or rescheduled_by.email,
            'old_date': old_date_time.strftime('%d/%m/%Y'),
            'old_time': old_date_time.strftime('%H:%M'),
            'new_date': appointment.date_time.strftime('%d/%m/%Y'),
            'new_time': appointment.date_time.strftime('%H:%M'),
            'site_url': site_url,
            'appointment_url': appointment_url,
        }
        
        html_content = render_to_string('emails/appointment_rescheduled.html', context)
        text_content = render_to_string('emails/appointment_rescheduled.txt', context)
        
        subject = _("Report de rendez-vous - %(date)s") % {'date': context['new_date']}
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        email.send()
        
        log_info(
            _("Appointment rescheduled email sent to %(email)s") % {'email': recipient.email},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return True
        
    except Exception as e:
        log_error(
            _("Error sending appointment rescheduled email: %(error)s") % {'error': e},
            exc_info=True,
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False


def send_appointment_request_email(appointment, recipient=None):
    """
    Envoie un email de demande de rendez-vous au conseiller.
    
    Args:
        appointment: Instance Appointment (demande)
        recipient: Utilisateur destinataire (par défaut: le conseiller)
        
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    if recipient is None:
        recipient = appointment.conseiller
    
    if not recipient.email:
        log_warning(
            _("Cannot send email: recipient %(user)s has no email address") % {'user': recipient.username},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False
    
    try:
        user_language = getattr(recipient, 'profile', None)
        if user_language and hasattr(user_language, 'language'):
            lang_code = user_language.language
            if lang_code and '-' in lang_code:
                lang_code = lang_code.split('-')[0]
            activate(lang_code)
        else:
            activate('fr')
        
        site_url = os.getenv('SITE_URL', 'http://localhost:8000')
        lang_code = get_language() or 'fr'
        appointment_url = f"{site_url}/{lang_code}{reverse('insurance_web:appointment_detail', args=[appointment.id])}"
        
        context = {
            'appointment': appointment,
            'recipient': recipient,
            'client': appointment.client,
            'client_name': appointment.client.get_full_name() or appointment.client.email,
            'appointment_date': appointment.date_time.strftime('%d/%m/%Y'),
            'appointment_time': appointment.date_time.strftime('%H:%M'),
            'site_url': site_url,
            'appointment_url': appointment_url,
        }
        
        html_content = render_to_string('emails/appointment_request.html', context)
        text_content = render_to_string('emails/appointment_request.txt', context)
        
        subject = _("Nouvelle demande de rendez-vous - %(date)s") % {'date': context['appointment_date']}
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        email.attach_alternative(html_content, "text/html")
        
        email.send()
        
        log_info(
            _("Appointment request email sent to %(email)s") % {'email': recipient.email},
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return True
        
    except Exception as e:
        log_error(
            _("Error sending appointment request email: %(error)s") % {'error': e},
            exc_info=True,
            extra={'appointment_id': appointment.id, 'recipient_id': recipient.id}
        )
        return False
