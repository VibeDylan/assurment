from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    SMOKER_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    REGION_CHOICES = [
        ('northwest', 'Northwest'),
        ('northeast', 'Northeast'),
        ('southwest', 'Southwest'),
        ('southeast', 'Southeast'),
    ]
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('conseiller', 'Advisor'),
        ('admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user',
        verbose_name="Role"
    )
    
    age = models.IntegerField(null=True, blank=True, verbose_name="Age")
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, null=True, blank=True, verbose_name="Gender")
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="BMI (Body Mass Index)")
    children = models.IntegerField(default=0, verbose_name="Number of Children")
    smoker = models.CharField(max_length=3, choices=SMOKER_CHOICES, null=True, blank=True, verbose_name="Smoker")
    region = models.CharField(max_length=20, choices=REGION_CHOICES, null=True, blank=True, verbose_name="Region")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
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
        verbose_name="Advisor"
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='appointments_as_client',
        verbose_name="Client"
    )
    date_time = models.DateTimeField(verbose_name="Date and Time")
    duration_minutes = models.IntegerField(default=60, verbose_name="Duration (minutes)")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['date_time']
    
    def __str__(self):
        return f"Appointment {self.conseiller.username} - {self.client.username} - {self.date_time.strftime('%m/%d/%Y %H:%M')}"

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions_created_by')
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(null=True, blank=True, verbose_name="Age")
    sex = models.CharField(max_length=10, choices=Profile.SEX_CHOICES, null=True, blank=True, verbose_name="Gender")
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="BMI (Body Mass Index)")
    children = models.IntegerField(default=0, verbose_name="Number of Children")
    smoker = models.CharField(max_length=3, choices=Profile.SMOKER_CHOICES, null=True, blank=True, verbose_name="Smoker")
    region = models.CharField(max_length=20, choices=Profile.REGION_CHOICES, null=True, blank=True, verbose_name="Region")

    class Meta: 
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"
        ordering = ['created_at']

    def __str__(self):
        return f"Prediction for {self.user.username} - {self.predicted_amount} €"
