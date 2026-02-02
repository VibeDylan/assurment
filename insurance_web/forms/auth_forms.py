from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from ..constants import SEX_CHOICES, SMOKER_CHOICES, REGION_CHOICES
from ..models import Profile


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Enter your first name'),
            'autocomplete': 'first-name'
        })
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Enter your last name'),
            'autocomplete': 'last-name'
        })
    )

    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Enter your email'),
            'autocomplete': 'email'
        })
    )
    
    password1 = forms.CharField(
        label=_("Password"),
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Create a password'),
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label=_("Confirm Password"),
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Confirm your password'),
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None
            if field_name == 'password1':
                self.fields[field_name].validators = []
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise forms.ValidationError(_("Password must contain at least 8 characters."))
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("The two passwords do not match."))
        return password2
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with this email already exists."))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        user.email = email
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Formulaire pour éditer le profil utilisateur"""
    
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter your first name'),
            'autocomplete': 'first-name'
        })
    )
    
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter your last name'),
            'autocomplete': 'last-name'
        })
    )
    
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': _('Enter your email'),
            'autocomplete': 'email'
        })
    )
    
    age = forms.IntegerField(
        label=_("Age"),
        required=False,
        min_value=18,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'placeholder': _('e.g. 40')
        })
    )
    
    sex = forms.ChoiceField(
        label=_("Gender"),
        choices=[('', _('---------'))] + list(SEX_CHOICES),
        required=False,
        widget=forms.Select()
    )
    
    height = forms.DecimalField(
        label=_("Taille (m)"),
        required=False,
        min_value=1.0,
        max_value=2.5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': _('e.g. 1.75'),
            'step': '0.01'
        })
    )
    
    weight = forms.DecimalField(
        label=_("Poids (kg)"),
        required=False,
        min_value=40.0,
        max_value=150.0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': _('e.g. 70'),
            'step': '0.1'
        })
    )
    
    children = forms.IntegerField(
        label=_("Number of Children"),
        required=False,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'placeholder': _('e.g. 2')
        })
    )
    
    def clean_children(self):
        """Assure que children a toujours une valeur par défaut de 0 si vide"""
        children = self.cleaned_data.get('children')
        return children if children is not None else 0
    
    smoker = forms.ChoiceField(
        label=_("Smoker"),
        choices=[('', _('---------'))] + list(SMOKER_CHOICES),
        required=False,
        widget=forms.Select()
    )
    
    region = forms.ChoiceField(
        label=_("Region"),
        choices=[('', _('---------'))] + list(REGION_CHOICES),
        required=False,
        widget=forms.Select()
    )
    
    additional_info = forms.CharField(
        label=_("Additional Information"),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Enter any additional information (optional)'),
            'rows': 4
        })
    )
    
    class Meta:
        model = Profile
        fields = ['age', 'sex', 'height', 'weight', 'children', 'smoker', 'region', 'additional_info']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pré-remplir les champs User si un utilisateur est fourni
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = getattr(self, 'user', None)
        if user:
            # Vérifier si l'email existe déjà pour un autre utilisateur
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                raise forms.ValidationError(_("A user with this email already exists."))
        return email
