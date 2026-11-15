import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from doctors.models import Doctor


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждена'
        COMPLETED = 'completed', 'Приём завершён'
        CANCELLED = 'cancelled', 'Отменена'

    ACTIVE_STATUSES = (Status.PENDING, Status.CONFIRMED)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', verbose_name='Аккаунт пациента')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments', verbose_name='Врач')
    patient_name = models.CharField('ФИО пациента', max_length=255)
    phone = models.CharField('Телефон', max_length=30, blank=True)
    reason = models.TextField('Жалобы / причина обращения', blank=True)
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.PENDING)
    doctor_notes = models.TextField(
        'Заключение врача', blank=True,
        help_text='Диагноз, назначения и рекомендации. Пациент видит их в своей записи.',
    )
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Изменена', auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        constraints = [
            # Один врач — одно активное время. Отменённые записи слот не занимают.
            models.UniqueConstraint(
                fields=['doctor', 'date', 'time'],
                condition=~models.Q(status='cancelled'),
                name='unique_active_slot',
            ),
        ]

    def __str__(self):
        return f'{self.patient_name} → {self.doctor} ({self.date:%d.%m.%Y} {self.time:%H:%M})'

    def get_absolute_url(self):
        return reverse('appointments:detail', args=[self.pk])

    @property
    def starts_at(self):
        return timezone.make_aware(datetime.datetime.combine(self.date, self.time))

    @property
    def is_upcoming(self):
        return self.starts_at >= timezone.now()

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES

    @property
    def can_cancel(self):
        return self.is_active and self.is_upcoming
