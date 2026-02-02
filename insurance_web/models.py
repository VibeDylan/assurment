from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .constants import SEX_CHOICES, SMOKER_CHOICES, REGION_CHOICES, ROLE_CHOICES, APPOINTMENT_STATUS_CHOICES, NOTIFICATION_TYPE_CHOICES

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
    type = models.CharField(choices=NOTIFICATION_TYPE_CHOICES, verbose_name=_("Type"))
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