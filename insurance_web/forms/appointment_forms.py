from django import forms


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
