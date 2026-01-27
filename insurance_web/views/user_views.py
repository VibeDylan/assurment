from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from ..forms import CustomUserCreationForm, PredictionForm, AppointmentForm
from ..models import Appointment, Profile, Prediction
from ..prediction_service import calculate_insurance_premium


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('insurance_web:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentification/signup.html', {'form': form})


@login_required
def profile(request):
    predictions_list = Prediction.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(predictions_list, 10)  
    page_number = request.GET.get('page')
    predictions = paginator.get_page(page_number)
    return render(request, 'authentification/profile.html', {'user': request.user, 'predictions': predictions})


def logout_view(request):
    logout(request)
    return redirect('insurance_web:home')


@login_required
def predict(request):
    profile = request.user.profile
    predicted_amount = None
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            predicted_amount = calculate_insurance_premium(form_data)
            prediction = Prediction.objects.create(
                user=request.user,
                created_by=request.user,
                predicted_amount=predicted_amount,
                age=form_data['age'],
                sex=form_data['sex'],
                bmi=form_data['bmi'],
                children=form_data['children'],
                smoker=form_data['smoker'],
                region=form_data['region']
            )
            profile.age = form_data['age']
            profile.sex = form_data['sex']
            profile.bmi = form_data['bmi']
            profile.children = form_data['children']
            profile.smoker = form_data['smoker']
            profile.region = form_data['region']
            profile.save()
            messages.success(request, f'Your estimated insurance premium is {predicted_amount:.2f} € per year.')
    else:
        initial_data = {}
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
    return render(request, 'predict.html', {
        'form': form,
        'predicted_amount': predicted_amount,
        'profile': profile
    })


@login_required
def conseillers_list(request):
    conseillers = User.objects.filter(profile__role='conseiller')
    return render(request, 'conseillers_list.html', {
        'conseillers': conseillers,
    })


@login_required
def conseiller_availability(request, conseiller_id):
    conseiller = get_object_or_404(User, id=conseiller_id, profile__role='conseiller')
    
    existing_appointments = Appointment.objects.filter(
        conseiller=conseiller,
        date_time__gte=timezone.now()
    ).order_by('date_time')
    
    date_filter = request.GET.get('date')
    selected_date = None
    available_slots = []
    
    if date_filter:
        try:
            selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            start_datetime = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
            end_datetime = start_datetime + timedelta(days=1)
            
            booked_slots = set()
            for apt in existing_appointments.filter(
                date_time__gte=start_datetime,
                date_time__lt=end_datetime
            ):
                slot_start = apt.date_time.replace(minute=0, second=0, microsecond=0)
                for i in range(apt.duration_minutes // 30):
                    booked_slots.add(slot_start + timedelta(minutes=i * 30))
            
            start_hour = 9
            end_hour = 18
            current_slot = start_datetime.replace(hour=start_hour)
            
            while current_slot.hour < end_hour:
                if current_slot not in booked_slots and current_slot > timezone.now():
                    available_slots.append(current_slot)
                current_slot += timedelta(minutes=30)
        except ValueError:
            pass
    
    return render(request, 'conseiller_availability.html', {
        'conseiller': conseiller,
        'existing_appointments': existing_appointments,
        'selected_date': selected_date,
        'available_slots': available_slots,
    })


@login_required
def create_appointment(request, conseiller_id):
    conseiller = get_object_or_404(User, id=conseiller_id, profile__role='conseiller')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            date_time = form.cleaned_data['date_time']
            duration_minutes = form.cleaned_data['duration_minutes']
            notes = form.cleaned_data.get('notes', '')
            
            if date_time <= timezone.now():
                messages.error(request, 'You cannot book a time slot in the past.')
            else:
                conflicting_appointments = Appointment.objects.filter(
                    conseiller=conseiller,
                    date_time__lt=date_time + timedelta(minutes=duration_minutes),
                    date_time__gte=date_time - timedelta(minutes=duration_minutes)
                )
                
                if conflicting_appointments.exists():
                    messages.error(request, 'This time slot is no longer available. Please choose another one.')
                else:
                    appointment = Appointment.objects.create(
                        conseiller=conseiller,
                        client=request.user,
                        date_time=date_time,
                        duration_minutes=duration_minutes,
                        notes=notes
                    )
                    messages.success(request, f'Appointment confirmed with {conseiller.get_full_name() or conseiller.username} on {date_time.strftime("%B %d, %Y at %H:%M")}.')
                    return redirect('insurance_web:my_appointments')
    else:
        form = AppointmentForm()
    
    return render(request, 'create_appointment.html', {
        'conseiller': conseiller,
        'form': form,
    })


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(
        client=request.user
    ).order_by('date_time')
    
    upcoming = appointments.filter(date_time__gte=timezone.now())
    past = appointments.filter(date_time__lt=timezone.now())
    
    return render(request, 'my_appointments.html', {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
    })
