class InsuranceWebException(Exception):
    """Exception de base pour l'application"""
    pass


class PredictionError(InsuranceWebException):
    """Erreur lors du calcul ou de la création d'une prédiction"""
    pass


class ModelNotFoundError(PredictionError):
    """Le modèle ML n'a pas été trouvé"""
    pass


class InvalidPredictionDataError(PredictionError):
    """Les données de prédiction sont invalides"""
    pass


class AppointmentError(InsuranceWebException):
    """Erreur lors de la création ou gestion d'un rendez-vous"""
    pass


class AppointmentConflictError(AppointmentError):
    """Conflit avec un rendez-vous existant"""
    pass
