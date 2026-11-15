import datetime

from django.conf import settings
from django.utils import timezone

from .models import Appointment


def booking_window():
    today = timezone.localdate()
    return today, today + datetime.timedelta(days=settings.BOOKING_DAYS_AHEAD)


def get_slots(doctor, day):
    hours = next((wh for wh in doctor.working_hours.all() if wh.weekday == day.weekday()), None)
    if hours is None:
        return []

    taken = set(
        Appointment.objects.filter(doctor=doctor, date=day)
        .exclude(status=Appointment.Status.CANCELLED)
        .values_list('time', flat=True)
    )
    now = timezone.localtime()
    step = datetime.timedelta(minutes=doctor.slot_minutes)
    current = datetime.datetime.combine(day, hours.start_time)
    end = datetime.datetime.combine(day, hours.end_time)

    slots = []
    while current + step <= end:
        t = current.time()
        if not (day == now.date() and t <= now.time()):
            slots.append({'time': t, 'free': t not in taken})
        current += step
    return slots


def get_free_times(doctor, day):
    return [s['time'] for s in get_slots(doctor, day) if s['free']]


def get_booking_days(doctor):
    start, end = booking_window()
    workdays = {wh.weekday for wh in doctor.working_hours.all()}
    days = []
    day = start
    while day <= end:
        if day.weekday() in workdays:
            free = len(get_free_times(doctor, day))
            days.append({'date': day, 'free': free})
        day += datetime.timedelta(days=1)
    return days


def next_free_day(doctor):
    for d in get_booking_days(doctor):
        if d['free']:
            return d['date']
    return None
