from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.isvalid():
            user = form.save()
            login(request, user)
            return redirect('insurance_web:home')

    else:
        form = UserCreationForm()
    return render(request, 'authentification/signup.html', {'form': form})