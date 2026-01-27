from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        })
    )
    
    password1 = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password'
        })
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'Confirm your password',
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
            if field_name == 'password1':
                self.fields[field_name].validators = []
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise forms.ValidationError("Password must contain at least 8 characters.")
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two passwords do not match.")
        return password2


class PredictionForm(forms.Form):
    age = forms.IntegerField(
        label="Age",
        required=True,
        min_value=18,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'e.g. 40'
        })
    )
    
    sex = forms.ChoiceField(
        label="Gender",
        choices=Profile.SEX_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    
    bmi = forms.DecimalField(
        label="BMI (Body Mass Index)",
        required=True,
        max_digits=5,
        decimal_places=2,
        min_value=10.0,
        max_value=50.0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'e.g. 22.5',
            'step': '0.1'
        })
    )
    
    children = forms.IntegerField(
        label="Number of Children",
        required=True,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'e.g. 2'
        })
    )
    
    smoker = forms.ChoiceField(
        label="Smoker",
        choices=Profile.SMOKER_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    
    region = forms.ChoiceField(
        label="Region",
        choices=Profile.REGION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )


class AppointmentForm(forms.Form):
    date_time = forms.DateTimeField(
        label="Date and Time",
        required=True,
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'type': 'datetime-local'
        })
    )
    duration_minutes = forms.IntegerField(
        label="Duration (minutes)",
        required=True,
        min_value=15,
        max_value=240,
        initial=60,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': '60'
        })
    )
    notes = forms.CharField(
        label="Notes (optional)",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'rows': 4,
            'placeholder': 'Additional information...'
        })
    )
