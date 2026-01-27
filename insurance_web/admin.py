from django.contrib import admin
from .models import Profile, Appointment

# Note: L'accès à Django admin nécessite is_staff=True ou is_superuser=True sur le User.
# Ceci est distinct du rôle 'admin' dans Profile.role qui est utilisé pour les permissions
# de l'application Assurement (gestion des utilisateurs, etc.).


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'age', 'sex', 'region', 'created_at')
    list_filter = ('role', 'sex', 'region', 'smoker')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('conseiller', 'client', 'date_time', 'duration_minutes', 'created_at')
    list_filter = ('date_time', 'conseiller')
    search_fields = ('conseiller__email', 'conseiller__first_name', 'conseiller__last_name', 'client__email', 'client__first_name', 'client__last_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date_time'
