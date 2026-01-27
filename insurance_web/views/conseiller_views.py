from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, date, timedelta
from calendar import monthrange
from ..utils.decorators import conseiller_required
from ..forms import PredictionForm
from ..models import Appointment, Prediction
from ..prediction_service import calculate_insurance_premium


@conseiller_required
def conseiller_dashboard(request):
    conseiller = request.user
    # If admin, show all appointments; if conseiller, only their appointments
    if request.user.profile.is_admin():
        total_appointments = Appointment.objects.count()
        upcoming_appointments = Appointment.objects.filter(
            date_time__gte=datetime.now()
        ).count()
        next_appointments = Appointment.objects.filter(
            date_time__gte=datetime.now()
        ).order_by('date_time')[:5]
    else:
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
            prediction = Prediction.objects.create(
                user=client,
                created_by=request.user,
                predicted_amount=predicted_amount,
                age=form_data['age'],
                sex=form_data['sex'],
                bmi=form_data['bmi'],
                children=form_data['children'],
                smoker=form_data['smoker'],
                region=form_data['region']
            )
            if client:
                client.profile.age = form_data['age']
                client.profile.sex = form_data['sex']
                client.profile.bmi = form_data['bmi']
                client.profile.children = form_data['children']
                client.profile.smoker = form_data['smoker']
                client.profile.region = form_data['region']
                client.profile.save()
            messages.success(request, f'Estimated premium: {predicted_amount:.2f} € per year')
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
    
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if year and month:
        try:
            current_date = date(int(year), int(month), 1)
        except (ValueError, TypeError):
            current_date = date.today().replace(day=1)
    else:
        current_date = date.today().replace(day=1)
    
    first_day = current_date.replace(day=1)
    last_day_num = monthrange(current_date.year, current_date.month)[1]
    last_day = current_date.replace(day=last_day_num)
    
    # If admin, show all appointments; if conseiller, only their appointments
    if request.user.profile.is_admin():
        appointments = Appointment.objects.filter(
            date_time__date__gte=first_day,
            date_time__date__lte=last_day
        ).order_by('date_time')
    else:
        appointments = Appointment.objects.filter(
            conseiller=conseiller,
            date_time__date__gte=first_day,
            date_time__date__lte=last_day
        ).order_by('date_time')
    
    appointments_by_date = {}
    for appointment in appointments:
        day = appointment.date_time.date()
        if day not in appointments_by_date:
            appointments_by_date[day] = []
        appointments_by_date[day].append(appointment)
    
    first_weekday = first_day.weekday()
    calendar_days = []
    
    if first_weekday > 0:
        prev_month = first_day - timedelta(days=first_weekday)
        for i in range(first_weekday):
            day = prev_month + timedelta(days=i)
            calendar_days.append({'date': day, 'is_current_month': False, 'appointments': []})
    
    for day_num in range(1, last_day_num + 1):
        day = current_date.replace(day=day_num)
        calendar_days.append({
            'date': day,
            'is_current_month': True,
            'appointments': appointments_by_date.get(day, [])
        })
    
    remaining_days = 42 - len(calendar_days)
    if remaining_days > 0:
        next_month = last_day + timedelta(days=1)
        for i in range(remaining_days):
            day = next_month + timedelta(days=i)
            calendar_days.append({'date': day, 'is_current_month': False, 'appointments': []})
    
    if current_date.month == 1:
        prev_month = current_date.replace(year=current_date.year - 1, month=12)
    else:
        prev_month = current_date.replace(month=current_date.month - 1)
    
    if current_date.month == 12:
        next_month = current_date.replace(year=current_date.year + 1, month=1)
    else:
        next_month = current_date.replace(month=current_date.month + 1)
    
    all_appointments_list = list(appointments)
    
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    return render(request, 'conseiller/calendar.html', {
        'calendar_days': calendar_days,
        'current_date': current_date,
        'month_name': month_names[current_date.month],
        'year': current_date.year,
        'prev_month': prev_month,
        'next_month': next_month,
        'today': date.today(),
        'all_appointments': all_appointments_list,
    })


@conseiller_required
def conseiller_clients_list(request):
    conseiller = request.user
    # If admin, show all appointments; if conseiller, only their appointments
    if request.user.profile.is_admin():
        clients_with_appointments = User.objects.filter(
            appointments_as_client__isnull=False
        ).distinct()
        all_users = User.objects.exclude(id=conseiller.id).exclude(profile__role='conseiller')
    else:
        clients_with_appointments = User.objects.filter(
            appointments_as_client__conseiller=conseiller
        ).distinct()
        all_users = User.objects.exclude(id=conseiller.id).exclude(profile__role='conseiller').exclude(profile__role='admin')
    return render(request, 'conseiller/clients_list.html', {
        'clients': clients_with_appointments,
        'all_users': all_users,
    })
