from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .constants import SEX_CHOICES, SMOKER_CHOICES, REGION_CHOICES, ROLE_CHOICES, APPOINTMENT_STATUS_CHOICES, NOTIFICATION_TYPE_CHOICES, UNAVAILABILITY_REASON_CHOICES

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=ROLE_CHOICES[0][0],
        verbose_name=_("Role")
    )
    
    age = models.IntegerField(null=True, blank=True, verbose_name=_("Age"))
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True, verbose_name=_("Gender"))
    height = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name=_("Height (m)"))
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Weight (kg)"))
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("BMI (Body Mass Index)"))
    children = models.IntegerField(default=0, verbose_name=_("Number of Children"))
    smoker = models.CharField(max_length=3, choices=SMOKER_CHOICES, null=True, blank=True, verbose_name=_("Smoker"))
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True, verbose_name=_("Region"))
    additional_info = models.TextField(null=True, blank=True, verbose_name=_("Additional Information"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
    
    def __str__(self):
        return _("Profile of %(name)s") % {'name': self.user.get_full_name() or self.user.email}
    
    def is_user(self):
        return self.role == ROLE_CHOICES[0][0]
    
    def is_conseiller(self):
        return self.role == ROLE_CHOICES[1][0]
    
    def is_admin(self):
        return self.role == ROLE_CHOICES[2][0]
    
    def can_make_prediction_for_others(self):
        return self.is_conseiller() or self.is_admin()
    
    def can_view_calendar(self):
        return self.is_conseiller() or self.is_admin()
    
    def can_view_all_profiles(self):
        return self.is_conseiller() or self.is_admin()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Appointment(models.Model):
    conseiller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='appointments_as_conseiller',
        verbose_name=_("Advisor")
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='appointments_as_client',
        verbose_name=_("Client")
    )
    date_time = models.DateTimeField(verbose_name=_("Date and Time"))
    duration_minutes = models.IntegerField(default=60, verbose_name=_("Duration (minutes)"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default=APPOINTMENT_STATUS_CHOICES[0][0], verbose_name=_("Status"))
    
    class Meta:
        verbose_name = _("Appointment")
        verbose_name_plural = _("Appointments")
        ordering = ['date_time']
    
    def __str__(self):
        conseiller_name = self.conseiller.get_full_name() or self.conseiller.email
        client_name = self.client.get_full_name() or self.client.email
        return _("Appointment %(conseiller)s - %(client)s - %(date)s") % {
            'conseiller': conseiller_name,
            'client': client_name,
            'date': self.date_time.strftime('%m/%d/%Y %H:%M')
        }


class ConseillerUnavailability(models.Model):
    """Indisponibilité du conseiller (vacances, maladie, formation, etc.)."""
    conseiller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='unavailabilities',
        verbose_name=_("Advisor"),
    )
    start_datetime = models.DateTimeField(verbose_name=_("Start"))
    end_datetime = models.DateTimeField(verbose_name=_("End"))
    reason = models.CharField(
        max_length=20,
        choices=UNAVAILABILITY_REASON_CHOICES,
        default='other',
        blank=True,
        verbose_name=_("Reason"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Unavailability")
        verbose_name_plural = _("Unavailabilities")
        ordering = ['start_datetime']

    def __str__(self):
        return _("%(conseiller)s unavailable %(start)s - %(end)s") % {
            'conseiller': self.conseiller.get_full_name() or self.conseiller.email,
            'start': self.start_datetime.strftime('%d/%m/%Y %H:%M'),
            'end': self.end_datetime.strftime('%d/%m/%Y %H:%M'),
        }


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions_created_by')
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(null=True, blank=True, verbose_name=_("Age"))
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True, verbose_name=_("Gender"))
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("BMI (Body Mass Index)"))
    children = models.IntegerField(default=0, verbose_name=_("Number of Children"))
    smoker = models.CharField(max_length=3, choices=SMOKER_CHOICES, null=True, blank=True, verbose_name=_("Smoker"))
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True, verbose_name=_("Region"))

    class Meta: 
        verbose_name = _("Prediction")
        verbose_name_plural = _("Predictions")
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.get_full_name() or self.user.email
        return _("Prediction for %(user)s - %(amount)s €") % {
            'user': user_name,
            'amount': self.predicted_amount
        }


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES, verbose_name=_("Type"))
    message = models.TextField(verbose_name=_("Message"))
    read = models.BooleanField(default=False, verbose_name=_("Read"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.get_full_name() or self.user.email
        if self.appointment:
            return _("Notification for %(user)s - %(appointment)s") % {
                'user': user_name,
                'appointment': self.appointment.date_time.strftime('%m/%d/%Y %H:%M')
            }
        return _("Notification for %(user)s") % {'user': user_name}


class PricingConfiguration(models.Model):
    """
    Configuration globale des prix (singleton).
    Une seule instance doit exister dans la base de données.
    """
    monthly_base_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00,
        verbose_name=_("Monthly Base Fee (€)"),
        help_text=_("Frais fixes mensuels en euros")
    )
    additional_charges_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Additional Charges Percentage (%)"),
        help_text=_("Pourcentage de charges supplémentaires à appliquer (ex: 15 pour 15%)")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Active ou désactive l'application de cette configuration")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Pricing Configuration")
        verbose_name_plural = _("Pricing Configurations")
        ordering = ['-created_at']

    def __str__(self):
        status = _("Active") if self.is_active else _("Inactive")
        return _("Pricing Configuration (%(status)s)") % {'status': status}

    def save(self, *args, **kwargs):
        """S'assure qu'il n'y a qu'une seule instance active"""
        if self.is_active:
            PricingConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_config(cls):
        """Récupère la configuration active ou crée une par défaut"""
        config = cls.objects.filter(is_active=True).first()
        if not config:
            config = cls.objects.create(
                monthly_base_fee=500.00,
                additional_charges_percentage=0.00,
                is_active=True
            )
        return config