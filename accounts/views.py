from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from appointments.models import Appointment

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html',{'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})

    return render(request, 'login.html')



@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'profile.html', {
        'user': request.user,
        'appointments': appointments
    })
# Create your views here.ё121   ёК2Й
