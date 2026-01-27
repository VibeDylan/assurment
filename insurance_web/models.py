from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    SEX_CHOICES = [
        ('male', 'Homme'),
        ('female', 'Femme'),
    ]
    
    SMOKER_CHOICES = [
        ('yes', 'Oui'),
        ('no', 'Non'),
    ]
    
    REGION_CHOICES = [
        ('northwest', 'Nord-Ouest'),
        ('northeast', 'Nord-Est'),
        ('southwest', 'Sud-Ouest'),
        ('southeast', 'Sud-Est'),
    ]
    
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('conseiller', 'Conseiller'),
        ('admin', 'Administrateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user',
        verbose_name="Rôle"
    )
    
    age = models.IntegerField(null=True, blank=True, verbose_name="Âge")
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True, verbose_name="Sexe")
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="BMI (Body Mass Index)")
    children = models.IntegerField(default=0, verbose_name="Nombre d'enfants")
    smoker = models.CharField(max_length=3, choices=SMOKER_CHOICES, null=True, blank=True, verbose_name="Fumeur")
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True, verbose_name="Région")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def is_user(self):
        return self.role == 'user'
    
    def is_conseiller(self):
        return self.role == 'conseiller'
    
    def is_admin(self):
        return self.role == 'admin'
    
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
        verbose_name="Conseiller"
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='appointments_as_client',
        verbose_name="Client"
    )
    date_time = models.DateTimeField(verbose_name="Date et heure")
    duration_minutes = models.IntegerField(default=60, verbose_name="Durée (minutes)")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['date_time']
    
    def __str__(self):
        return f"RDV {self.conseiller.username} - {self.client.username} - {self.date_time.strftime('%d/%m/%Y %H:%M')}"