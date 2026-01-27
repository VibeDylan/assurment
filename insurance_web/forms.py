from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé avec labels en français.
    Sans messages d'aide pour un design épuré.
    """
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors',
            'placeholder': "Choisissez un nom d'utilisateur",
            'autocomplete': 'username'
        })
    )
    
    password1 = forms.CharField(
        label="Mot de passe",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors',
            'placeholder': 'Créez un mot de passe',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None
            # Supprimer les validateurs qui génèrent des messages d'aide
            if field_name == 'password1':
                # Remplacer les validateurs par une validation simple
                self.fields[field_name].validators = []
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        # Validation simple avec message court
        if len(password1) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return password2


class PredictionForm(forms.Form):
    """Formulaire pour la prédiction de prime d'assurance."""
    
    age = forms.IntegerField(
        label="Âge",
        required=True,
        min_value=18,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors',
            'placeholder': 'Ex: 40'
        })
    )
    
    sex = forms.ChoiceField(
        label="Sexe",
        choices=Profile.SEX_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors'
        })
    )
    
    bmi = forms.DecimalField(
        label="IMC (Indice de Masse Corporelle)",
        required=True,
        max_digits=5,
        decimal_places=2,
        min_value=10.0,
        max_value=50.0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors',
            'placeholder': 'Ex: 28.5',
            'step': '0.1'
        })
    )
    
    children = forms.IntegerField(
        label="Nombre d'enfants",
        required=True,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors',
            'placeholder': 'Ex: 2'
        })
    )
    
    smoker = forms.ChoiceField(
        label="Fumeur",
        choices=Profile.SMOKER_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors'
        })
    )
    
    region = forms.ChoiceField(
        label="Région",
        choices=Profile.REGION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors'
        })
    )
