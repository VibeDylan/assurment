from django import forms
from django.utils.translation import gettext_lazy as _
from ..constants import SEX_CHOICES, SMOKER_CHOICES, REGION_CHOICES


class PredictionForm(forms.Form):
    age = forms.IntegerField(
        label=_("Age"),
        required=True,
        min_value=18,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('e.g. 40')
        })
    )
    
    sex = forms.ChoiceField(
        label=_("Gender"),
        choices=SEX_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    

    height = forms.DecimalField(
        label=_("Height (in meters)"),
        required=True,
        min_value=1.0,
        max_value=2.5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('e.g. 1.75')
        })
    )

    weight = forms.DecimalField(
        label=_("Weight (in kilograms)"),
        required=True,
        min_value=40.0,
        max_value=150.0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('e.g. 70.0')
        })
    )

    children = forms.IntegerField(
        label=_("Number of Children"),
        required=True,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('e.g. 2')
        })
    )
    
    smoker = forms.ChoiceField(
        label=_("Smoker"),
        choices=SMOKER_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    
    region = forms.ChoiceField(
        label=_("Region"),
        choices=REGION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors'
        })
    )
    
    additional_info = forms.CharField(
        label=_("Informations complémentaires"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'placeholder': _('Entrez des informations complémentaires (optionnel)'),
            'rows': 4
        })
    )
