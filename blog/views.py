from django import forms
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from doctors.models import Doctor, Specialty, WorkingHours

from .models import ContactRequest


def _active_specialties():
    return Specialty.objects.filter(is_active=True).annotate(
        doctor_count=Count('doctors', filter=Q(doctors__is_active=True)),
    )


def home(request):
    specialties = _active_specialties()
    return render(request, 'home.html', {
        'specialties': specialties[:9],
        'specialty_total': specialties.count(),
        'doctors': Doctor.objects.filter(is_active=True).select_related('specialty').order_by('-experience')[:4],
        'doctor_total': Doctor.objects.filter(is_active=True).count(),
    })


def services(request):
    return render(request, 'services/list.html', {'specialties': _active_specialties()})


def specialty_detail(request, slug):
    specialty = get_object_or_404(Specialty, slug=slug, is_active=True)
    return render(request, 'services/detail.html', {
        'specialty': specialty,
        'doctors': specialty.doctors.filter(is_active=True),
        'others': _active_specialties().exclude(pk=specialty.pk)[:6],
    })


def schedule(request):
    doctors = (
        Doctor.objects.filter(is_active=True)
        .select_related('specialty').prefetch_related('working_hours')
        .order_by('specialty__order', 'name')
    )
    spec = request.GET.get('specialty', '')
    if spec:
        doctors = doctors.filter(specialty__slug=spec)
    rows = []
    for d in doctors:
        hours = {wh.weekday: wh for wh in d.working_hours.all()}
        rows.append((d, [hours.get(i) for i in range(7)]))
    return render(request, 'schedule.html', {
        'rows': rows,
        'weekdays': WorkingHours.SHORT,
        'specialties': Specialty.objects.filter(is_active=True, doctors__is_active=True).distinct(),
        'current_specialty': spec,
    })


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['name', 'phone', 'message']
        labels = {'name': 'Ваше имя', 'phone': 'Телефон / WhatsApp', 'message': 'Что вас беспокоит?'}
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+996 ___ ___ ___', 'inputmode': 'tel'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Кратко опишите вопрос — мы подберём нужного специалиста'}),
        }


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Заявка отправлена! Администратор свяжется с вами в рабочее время.')
        return redirect('contact')
    return render(request, 'contact.html', {'form': form})
