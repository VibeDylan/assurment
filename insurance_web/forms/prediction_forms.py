from django import forms
from ..constants import SEX_CHOICES, SMOKER_CHOICES, REGION_CHOICES


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
        choices=SEX_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    

    height = forms.DecimalField(
        label="Height (in meters)",
        required=True,
        min_value=1.0,
        max_value=2.5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'e.g. 1.75'
        })
    )

    weight = forms.DecimalField(
        label="Weight (in kilograms)",
        required=True,
        min_value=40.0,
        max_value=150.0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': 'e.g. 70.0'
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
        choices=SMOKER_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    
    region = forms.ChoiceField(
        label="Region",
        choices=REGION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
