import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm
from appointments.models import Appointment
from django.contrib.auth.models import User


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')


            verification_code = str(random.randint(1000, 9999))


            request.session['temp_user_data'] = {
                'username': username,
                'email': email,
                'password': password,
                'code': verification_code
            }


            send_mail(
                'MedEase: Подтвердите регистрацию',
                f'Ваш код подтверждения: {verification_code}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect('verify_code')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def verify_code_view(request):
    error = None

    temp_data = request.session.get('temp_user_data')

    if request.method == 'POST':
        user_code = request.POST.get('code')


        if temp_data and user_code == temp_data['code']:

            user = User.objects.create_user(
                username=temp_data['username'],
                email=temp_data['email'],
                password=temp_data['password']
            )
            login(request, user)


            if 'temp_user_data' in request.session:
                del request.session['temp_user_data']

            return redirect('home')
        else:
            error = ""

    return render(request, 'verify_code.html', {'error': error})


def resend_code_view(request):

    temp_data = request.session.get('temp_user_data')

    if temp_data:

        new_code = str(random.randint(1000, 9999))


        temp_data['code'] = new_code
        request.session['temp_user_data'] = temp_data
        request.session.modified = True

        send_mail(
            'MedEase: Подтвердите регистрацию',
            f'Ваш новый код подтверждения: {new_code}',
            settings.EMAIL_HOST_USER,
            [temp_data['email']],
            fail_silently=False,
        )
        return render(request, 'verify_code.html', {'message': 'На ваш электронный адрес отправлен новый код!'})

    return redirect('register')



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
    if request.method == "POST":
        logout(request)
        return redirect('home')

@login_required
def profile(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'profile.html', {
        'user': request.user,
        'appointments': appointments
    })

