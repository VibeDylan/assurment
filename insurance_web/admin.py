from django.contrib import admin
from .models import Profile, Appointment


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'age', 'sex', 'region', 'created_at')
    list_filter = ('role', 'sex', 'region', 'smoker')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('conseiller', 'client', 'date_time', 'duration_minutes', 'created_at')
    list_filter = ('date_time', 'conseiller')
    search_fields = ('conseiller__username', 'client__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date_time'
