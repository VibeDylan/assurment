from django.contrib import admin
from .models import Profile, Appointment, ConseillerUnavailability, PricingConfiguration


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'age', 'sex', 'region', 'created_at')
    list_filter = ('role', 'sex', 'region', 'smoker')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('conseiller', 'client', 'date_time', 'duration_minutes', 'status', 'created_at')
    list_filter = ('status', 'date_time', 'conseiller')
    search_fields = ('conseiller__email', 'conseiller__first_name', 'conseiller__last_name', 'client__email', 'client__first_name', 'client__last_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date_time'


@admin.register(ConseillerUnavailability)
class ConseillerUnavailabilityAdmin(admin.ModelAdmin):
    list_display = ('conseiller', 'start_datetime', 'end_datetime', 'reason', 'created_at')
    list_filter = ('reason', 'conseiller')
    search_fields = ('conseiller__email', 'notes')
    date_hierarchy = 'start_datetime'


@admin.register(PricingConfiguration)
class PricingConfigurationAdmin(admin.ModelAdmin):
    list_display = ('monthly_base_fee', 'additional_charges_percentage', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    fields = ('monthly_base_fee', 'additional_charges_percentage', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        if PricingConfiguration.objects.filter(is_active=True).exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_active:
            active_count = PricingConfiguration.objects.filter(is_active=True).count()
            if active_count <= 1:
                return False
        return super().has_delete_permission(request, obj)
