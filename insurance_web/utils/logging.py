import logging
import sys
from typing import Optional

logger = logging.getLogger('insurance_web')


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retourne un logger configuré pour le module spécifié.
    
    Args:
        name: Nom du module (optionnel). Si None, retourne le logger principal.
    
    Returns:
        logging.Logger: Logger configuré
    """
    if name:
        return logging.getLogger(f'insurance_web.{name}')
    return logger


def log_info(message: str, extra: Optional[dict] = None) -> None:
    """Log un message d'information"""
    logger.info(message, extra=extra or {})


def log_warning(message: str, extra: Optional[dict] = None) -> None:
    """Log un message d'avertissement"""
    logger.warning(message, extra=extra or {})


def log_error(message: str, exc_info: bool = False, extra: Optional[dict] = None) -> None:
    """
    Log un message d'erreur.
    
    Args:
        message: Message d'erreur
        exc_info: Si True, inclut la traceback complète
        extra: Contexte supplémentaire (user_id, request_path, etc.)
    """
    logger.error(message, exc_info=exc_info, extra=extra or {})


def log_critical(message: str, exc_info: bool = True, extra: Optional[dict] = None) -> None:
    """
    Log un message critique (erreur grave).
    
    Args:
        message: Message critique
        exc_info: Si True, inclut la traceback complète
        extra: Contexte supplémentaire
    """
    logger.critical(message, exc_info=exc_info, extra=extra or {})


def log_user_action(user, action: str, details: Optional[dict] = None) -> None:
    """
    Log une action utilisateur importante.
    
    Args:
        user: Instance User Django
        action: Description de l'action (ex: "prediction_created", "appointment_booked")
        details: Détails supplémentaires de l'action
    """
    extra = {
        'user_id': user.id if user.is_authenticated else None,
        'username': user.username if user.is_authenticated else 'anonymous',
        'action': action,
    }
    if details:
        extra.update(details)
    logger.info(f"User action: {action}", extra=extra)


def log_prediction(user, predicted_amount: float, form_data: dict) -> None:
    """Log la création d'une prédiction"""
    log_user_action(
        user,
        'prediction_created',
        {
            'predicted_amount': predicted_amount,
            'age': form_data.get('age'),
            'region': form_data.get('region'),
        }
    )


def log_appointment(appointment, action: str = 'created') -> None:
    """Log une action sur un rendez-vous"""
    logger.info(
        f"Appointment {action}",
        extra={
            'appointment_id': appointment.id,
            'conseiller_id': appointment.conseiller.id,
            'client_id': appointment.client.id,
            'date_time': appointment.date_time.isoformat(),
            'action': f'appointment_{action}',
        }
    )
