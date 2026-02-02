from django import forms
from django.utils.translation import gettext_lazy as _



class AppointmentForm(forms.Form):
    date_time = forms.DateTimeField(
        label=_("Date and Time"),
        required=True,
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
                'type': 'datetime-local'
            }
        )
    )
    duration_minutes = forms.IntegerField(
        label=_("Duration (minutes)"),
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
        label=_("Notes (optional)"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-md text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            'rows': 4,
            'placeholder': _('Additional information...')
        })
    )


class UnavailabilityForm(forms.Form):
    start_datetime = forms.DateTimeField(
        label=_("Début"),
        required=True,
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'class': 'w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-gray-900 focus:border-primary focus:ring-2 focus:ring-primary/20',
                'type': 'datetime-local',
            }
        ),
    )
    end_datetime = forms.DateTimeField(
        label=_("Fin"),
        required=True,
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'class': 'w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-gray-900 focus:border-primary focus:ring-2 focus:ring-primary/20',
                'type': 'datetime-local',
            }
        ),
    )
    notes = forms.CharField(
        label=_("Notes (optionnel)"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/20',
            'rows': 2,
            'placeholder': _('Optionnel'),
        }),
    )
