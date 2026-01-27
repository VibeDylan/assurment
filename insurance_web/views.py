from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, PredictionForm
from .prediction_service import calculate_insurance_premium

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
    return render(request, 'authentification/profile.html', {'user': request.user})


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
            
            profile.age = form_data['age']
            profile.sex = form_data['sex']
            profile.bmi = form_data['bmi']
            profile.children = form_data['children']
            profile.smoker = form_data['smoker']
            profile.region = form_data['region']
            profile.save()
            
            messages.success(request, f'Votre prime d\'assurance estimée est de {predicted_amount:.2f} € par an.')
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