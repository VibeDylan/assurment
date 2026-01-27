from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from ..utils.decorators import conseiller_required
from ..forms import PredictionForm
from ..models import Appointment
from ..prediction_service import calculate_insurance_premium


@conseiller_required
def conseiller_dashboard(request):
    conseiller = request.user
    total_appointments = Appointment.objects.filter(conseiller=conseiller).count()
    upcoming_appointments = Appointment.objects.filter(
        conseiller=conseiller,
        date_time__gte=datetime.now()
    ).count()
    next_appointments = Appointment.objects.filter(
        conseiller=conseiller,
        date_time__gte=datetime.now()
    ).order_by('date_time')[:5]
    return render(request, 'conseiller/dashboard.html', {
        'total_appointments': total_appointments,
        'upcoming_appointments': upcoming_appointments,
        'next_appointments': next_appointments,
    })


@conseiller_required
def conseiller_predict_for_client(request, client_id=None):
    client = None
    predicted_amount = None
    if client_id:
        client = get_object_or_404(User, id=client_id)
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            predicted_amount = calculate_insurance_premium(form_data)
            if client:
                client.profile.age = form_data['age']
                client.profile.sex = form_data['sex']
                client.profile.bmi = form_data['bmi']
                client.profile.children = form_data['children']
                client.profile.smoker = form_data['smoker']
                client.profile.region = form_data['region']
                client.profile.save()
            messages.success(request, f'Prime estimée: {predicted_amount:.2f} € par an')
    else:
        initial_data = {}
        if client and client.profile:
            profile = client.profile
            if profile.age is not None:
                initial_data['age'] = profile.age
            if profile.sex:
                initial_data['sex'] = profile.sex
            if profile.bmi is not None:
                initial_data['bmi'] = profile.bmi
            if profile.children is not None:
                initial_data['children'] = profile.children
            if profile.smoker:
                initial_data['smoker'] = profile.smoker
            if profile.region:
                initial_data['region'] = profile.region
        form = PredictionForm(initial=initial_data)
    return render(request, 'conseiller/predict_for_client.html', {
        'form': form,
        'predicted_amount': predicted_amount,
        'client': client,
    })


@conseiller_required
def conseiller_calendar(request):
    conseiller = request.user
    appointments = Appointment.objects.filter(conseiller=conseiller)
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(date_time__date=filter_date)
        except ValueError:
            pass
    return render(request, 'conseiller/calendar.html', {
        'appointments': appointments,
    })


@conseiller_required
def conseiller_clients_list(request):
    conseiller = request.user
    clients = User.objects.filter(
        appointments_as_client__conseiller=conseiller
    ).distinct()
    return render(request, 'conseiller/clients_list.html', {
        'clients': clients,
    })
