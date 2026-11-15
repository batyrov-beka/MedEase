import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Profile
from doctors.models import Doctor

from .forms import BookingForm, DoctorNotesForm
from .models import Appointment
from .services import get_booking_days, get_slots

Status = Appointment.Status


def _parse_date(value):
    try:
        return datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(
        Doctor.objects.select_related('specialty').prefetch_related('working_hours'),
        pk=doctor_id, is_active=True,
    )
    days = get_booking_days(doctor)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = BookingForm(request.POST, doctor=doctor)
        selected = _parse_date(request.POST.get('date'))
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    appointment = Appointment.objects.create(
                        user=request.user, doctor=doctor,
                        patient_name=cd['patient_name'], phone=cd['phone'], reason=cd['reason'],
                        date=cd['date'], time=cd['time'],
                    )
            except IntegrityError:
                form.add_error(None, 'Кто-то только что занял это время. Выберите другое.')
            else:
                if not profile.phone:
                    profile.phone = cd['phone']
                    profile.save(update_fields=['phone'])
                _notify_booking(appointment)
                messages.success(request, 'Вы записаны! Ожидайте подтверждения от клиники.')
                return redirect(appointment)
    else:
        selected = _parse_date(request.GET.get('date'))
        form = BookingForm(doctor=doctor, initial={
            'patient_name': request.user.get_full_name(),
            'phone': profile.phone,
        })

    valid_dates = {d['date'] for d in days}
    if selected not in valid_dates:
        selected = next((d['date'] for d in days if d['free']), days[0]['date'] if days else None)

    return render(request, 'appointments/book.html', {
        'doctor': doctor,
        'form': form,
        'days': days,
        'selected_date': selected,
        'slots': get_slots(doctor, selected) if selected else [],
        'selected_time': request.POST.get('time', ''),
    })


def _notify_booking(appointment):
    email = appointment.user.email
    if not email:
        return
    send_mail(
        'MedEase: вы записаны на приём',
        (
            f'Здравствуйте, {appointment.patient_name}!\n\n'
            f'Вы записаны к врачу: {appointment.doctor.name} ({appointment.doctor.specialty}).\n'
            f'Дата и время: {appointment.date:%d.%m.%Y} в {appointment.time:%H:%M}.\n\n'
            'Статус записи можно посмотреть в разделе «Мои записи» на сайте.\n'
            'Если планы изменятся — пожалуйста, отмените запись заранее.'
        ),
        None, [email], fail_silently=True,
    )


@login_required
def my_appointments(request):
    now = timezone.localtime()
    qs = Appointment.objects.filter(user=request.user).select_related('doctor__specialty')
    upcoming = [a for a in qs.order_by('date', 'time') if a.is_active and a.is_upcoming]
    history = [a for a in qs if a not in upcoming]
    return render(request, 'appointments/my.html', {
        'upcoming': upcoming,
        'history': history,
        'now': now,
    })


def _get_for_user(request, pk):
    appointment = get_object_or_404(Appointment.objects.select_related('doctor__specialty', 'user'), pk=pk)
    doctor = getattr(request.user, 'doctor', None)
    is_owner = appointment.user_id == request.user.id
    is_doctor = doctor is not None and appointment.doctor_id == doctor.id
    if not (is_owner or is_doctor or request.user.is_staff):
        raise Http404
    return appointment, is_doctor or request.user.is_staff


@login_required
def appointment_detail(request, pk):
    appointment, can_manage = _get_for_user(request, pk)
    form = None
    if can_manage:
        form = DoctorNotesForm(request.POST or None, instance=appointment)
        if request.method == 'POST' and form.is_valid():
            form.save()
            if request.POST.get('complete') and appointment.status != Status.CANCELLED:
                appointment.status = Status.COMPLETED
                appointment.save(update_fields=['status', 'updated_at'])
                messages.success(request, 'Заключение сохранено, приём завершён.')
            else:
                messages.success(request, 'Заключение сохранено.')
            return redirect(appointment)

    patient_profile = Profile.objects.filter(user=appointment.user).first() if can_manage else None
    previous = (
        Appointment.objects.filter(user=appointment.user, status=Status.COMPLETED)
        .exclude(pk=appointment.pk).select_related('doctor__specialty')[:5]
        if can_manage else []
    )
    return render(request, 'appointments/detail.html', {
        'a': appointment,
        'can_manage': can_manage,
        'form': form,
        'patient_profile': patient_profile,
        'previous': previous,
    })


@login_required
@require_POST
def cancel_appointment(request, pk):
    appointment, can_manage = _get_for_user(request, pk)
    if appointment.is_active and (can_manage or appointment.is_upcoming):
        appointment.status = Status.CANCELLED
        appointment.save(update_fields=['status', 'updated_at'])
        messages.info(request, 'Запись отменена.')
    else:
        messages.error(request, 'Эту запись уже нельзя отменить.')
    return redirect(request.POST.get('next') or 'appointments:my')


@login_required
@require_POST
def set_status(request, pk):
    appointment, can_manage = _get_for_user(request, pk)
    if not can_manage:
        raise Http404
    new_status = request.POST.get('status')
    allowed = {
        Status.PENDING: {Status.CONFIRMED, Status.CANCELLED, Status.COMPLETED},
        Status.CONFIRMED: {Status.COMPLETED, Status.CANCELLED},
    }
    if new_status in allowed.get(appointment.status, set()):
        appointment.status = new_status
        appointment.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Статус изменён: {appointment.get_status_display().lower()}.')
    else:
        messages.error(request, 'Этот статус сейчас установить нельзя.')
    return redirect(request.POST.get('next') or 'doctors:dashboard')
