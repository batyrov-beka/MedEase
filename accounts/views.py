import secrets
import time

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from appointments.models import Appointment

from .forms import LoginForm, ProfileForm, RegisterForm, UserForm
from .models import Profile

CODE_TTL_SECONDS = 10 * 60
MAX_ATTEMPTS = 5
SESSION_KEY = 'pending_registration'


def _send_code(email, code):
    send_mail(
        'MedEase: код подтверждения',
        f'Ваш код подтверждения регистрации: {code}\n\nКод действует 10 минут. '
        'Если вы не регистрировались на сайте MedEase — просто проигнорируйте это письмо.',
        None, [email],
    )


def _new_code():
    return f'{secrets.randbelow(1_000_000):06d}'


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        code = _new_code()
        try:
            _send_code(cd['email'], code)
        except Exception:
            form.add_error('email', 'Не удалось отправить письмо. Проверьте адрес или попробуйте позже.')
        else:
            request.session[SESSION_KEY] = {
                'username': cd['username'],
                'first_name': cd['first_name'],
                'last_name': cd['last_name'],
                'email': cd['email'],
                'phone': cd.get('phone', ''),
                # В сессии храним только хеш пароля, не сам пароль
                'password_hash': make_password(cd['password1']),
                'code': code,
                'expires': time.time() + CODE_TTL_SECONDS,
                'attempts': 0,
            }
            return redirect('verify_code')
    return render(request, 'accounts/register.html', {'form': form})


def verify_code_view(request):
    data = request.session.get(SESSION_KEY)
    if not data:
        messages.info(request, 'Сначала заполните форму регистрации.')
        return redirect('register')

    error = None
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if time.time() > data['expires']:
            error = 'Срок действия кода истёк. Отправьте новый код.'
        elif data['attempts'] >= MAX_ATTEMPTS:
            error = 'Слишком много попыток. Отправьте новый код.'
        elif not secrets.compare_digest(code, data['code']):
            data['attempts'] += 1
            request.session[SESSION_KEY] = data
            error = f'Неверный код. Осталось попыток: {MAX_ATTEMPTS - data["attempts"]}.'
        elif User.objects.filter(username=data['username']).exists():
            del request.session[SESSION_KEY]
            messages.error(request, 'Этот логин уже занят. Зарегистрируйтесь ещё раз с другим логином.')
            return redirect('register')
        else:
            with transaction.atomic():
                user = User.objects.create(
                    username=data['username'], email=data['email'],
                    first_name=data['first_name'], last_name=data['last_name'],
                    password=data['password_hash'],
                )
                Profile.objects.create(user=user, phone=data['phone'])
            del request.session[SESSION_KEY]
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Добро пожаловать, {user.first_name}! Регистрация завершена.')
            return redirect('profile')

    return render(request, 'accounts/verify_code.html', {'error': error, 'email': data['email']})


@require_POST
def resend_code_view(request):
    data = request.session.get(SESSION_KEY)
    if not data:
        return redirect('register')
    data.update(code=_new_code(), expires=time.time() + CODE_TTL_SECONDS, attempts=0)
    try:
        _send_code(data['email'], data['code'])
    except Exception:
        messages.error(request, 'Не удалось отправить письмо. Попробуйте позже.')
    else:
        messages.success(request, 'Новый код отправлен на вашу почту.')
    request.session[SESSION_KEY] = data
    return redirect('verify_code')


class MedLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        if hasattr(self.request.user, 'doctor'):
            return reverse('doctors:dashboard')
        return reverse('profile')


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    appointments = Appointment.objects.filter(user=request.user).select_related('doctor__specialty')
    upcoming = [a for a in appointments.order_by('date', 'time') if a.is_active and a.is_upcoming]
    completed = appointments.filter(status=Appointment.Status.COMPLETED)
    return render(request, 'accounts/profile.html', {
        'profile': profile_obj,
        'upcoming': upcoming[:3],
        'upcoming_count': len(upcoming),
        'completed': completed[:5],
        'completed_count': completed.count(),
        'total_count': appointments.count(),
    })


@login_required
def profile_edit(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    user_form = UserForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=profile_obj)
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, 'Данные сохранены.')
        return redirect('profile')
    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
