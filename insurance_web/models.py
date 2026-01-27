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
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil lors de la création d'un utilisateur."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil lors de la sauvegarde de l'utilisateur."""
    if hasattr(instance, 'profile'):
        instance.profile.save()