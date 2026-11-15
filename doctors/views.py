from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from appointments.models import Appointment
from appointments.services import next_free_day

from .models import Doctor, Specialty, WorkingHours


def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True).select_related('specialty')
    specialties = Specialty.objects.filter(is_active=True, doctors__is_active=True).distinct()

    q = request.GET.get('q', '').strip()
    spec = request.GET.get('specialty', '')
    if q:
        doctors = doctors.filter(Q(name__icontains=q) | Q(specialty__name__icontains=q) | Q(position__icontains=q))
    if spec:
        doctors = doctors.filter(specialty__slug=spec)

    return render(request, 'doctors/list.html', {
        'doctors': doctors,
        'specialties': specialties,
        'q': q,
        'current_specialty': spec,
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.select_related('specialty').prefetch_related('working_hours'),
        pk=pk, is_active=True,
    )
    hours = {wh.weekday: wh for wh in doctor.working_hours.all()}
    week = [(WorkingHours.SHORT[i], name, hours.get(i)) for i, name in WorkingHours.WEEKDAYS]
    return render(request, 'doctors/detail.html', {
        'doctor': doctor,
        'week': week,
        'today_weekday': timezone.localdate().weekday(),
        'next_day': next_free_day(doctor) if hours else None,
        'related': Doctor.objects.filter(specialty=doctor.specialty, is_active=True).exclude(pk=doctor.pk)[:3],
    })


@login_required
def dashboard(request):
    doctor = getattr(request.user, 'doctor', None)
    if doctor is None:
        raise Http404('Панель доступна только врачам.')

    today = timezone.localdate()
    base = Appointment.objects.filter(doctor=doctor)
    tabs = {
        'today': ('Сегодня', base.filter(date=today).order_by('time')),
        'upcoming': ('Предстоящие', base.filter(date__gt=today, status__in=Appointment.ACTIVE_STATUSES).order_by('date', 'time')),
        'pending': ('Ждут подтверждения', base.filter(status=Appointment.Status.PENDING, date__gte=today).order_by('date', 'time')),
        'past': ('История', base.filter(date__lt=today).order_by('-date', '-time')),
    }
    tab = request.GET.get('tab', 'today')
    if tab not in tabs:
        tab = 'today'

    stats = base.aggregate(
        today=Count('id', filter=Q(date=today) & ~Q(status=Appointment.Status.CANCELLED)),
        pending=Count('id', filter=Q(status=Appointment.Status.PENDING, date__gte=today)),
        upcoming=Count('id', filter=Q(date__gte=today, status__in=Appointment.ACTIVE_STATUSES)),
        completed=Count('id', filter=Q(status=Appointment.Status.COMPLETED)),
    )
    return render(request, 'doctors/dashboard.html', {
        'doctor': doctor,
        'tabs': [(key, label, qs.count()) for key, (label, qs) in tabs.items()],
        'tab': tab,
        'appointments': tabs[tab][1].select_related('user'),
        'stats': stats,
        'today': today,
    })
