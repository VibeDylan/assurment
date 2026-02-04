from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from ..constants import ROLE_CHOICES


class AdminUserManagementForm(forms.Form):
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Enter first name'),
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Enter last name'),
            'autocomplete': 'family-name'
        })
    )
    
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Enter email address'),
            'autocomplete': 'email'
        })
    )
    
    password = forms.CharField(
        label=_("Password"),
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Enter password'),
            'autocomplete': 'new-password'
        }),
        min_length=8,
        help_text=_("Password must be at least 8 characters long.")
    )
    
    role = forms.ChoiceField(
        label=_("Role"),
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with this email already exists."))
        return email
    
    def save(self):
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        password = self.cleaned_data.get('password')
        role = self.cleaned_data.get('role')
        
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        user.profile.role = role
        user.profile.save()
        
        return user


class AdminUserRoleForm(forms.Form):
    role = forms.ChoiceField(
        label=_("Role"),
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )


class PricingConfigurationForm(forms.Form):
    monthly_base_fee = forms.DecimalField(
        label=_("Frais fixes mensuels (€)"),
        required=True,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-8 pr-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('e.g. 500.00'),
            'step': '0.01'
        }),
        help_text=_("Frais fixes mensuels ajoutés au prix mensuel de base (ex: 500 €)")
    )
    
    additional_charges_percentage = forms.DecimalField(
        label=_("Charges supplémentaires (%)"),
        required=True,
        min_value=0,
        max_value=100,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-4 pr-8 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('e.g. 15.00'),
            'step': '0.01'
        }),
        help_text=_("Pourcentage de charges supplémentaires à appliquer sur le prix mensuel (ex: 15 pour 15%)")
    )
    
    is_active = forms.BooleanField(
        label=_("Configuration active"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
        }),
        help_text=_("Active ou désactive l'application de cette configuration")
    )
    
    def save(self):
        """Sauvegarde ou met à jour la configuration de pricing"""
        from ..models import PricingConfiguration
        
        monthly_base_fee = self.cleaned_data.get('monthly_base_fee')
        additional_charges_percentage = self.cleaned_data.get('additional_charges_percentage')
        is_active = self.cleaned_data.get('is_active', True)
        
        # Récupérer la configuration active ou en créer une nouvelle
        config = PricingConfiguration.objects.filter(is_active=True).first()
        
        if not config:
            config = PricingConfiguration.objects.create(
                monthly_base_fee=monthly_base_fee,
                additional_charges_percentage=additional_charges_percentage,
                is_active=is_active
            )
        else:
            config.monthly_base_fee = monthly_base_fee
            config.additional_charges_percentage = additional_charges_percentage
            config.is_active = is_active
            config.save()
        
        return config
