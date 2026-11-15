from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Specialty(models.Model):
    """Медицинское направление (кардиология, педиатрия и т. д.)."""

    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('Адрес (slug)', max_length=100, unique=True)
    icon = models.CharField(
        'Иконка Font Awesome', max_length=50, default='fa-stethoscope',
        help_text='Например: fa-heart-pulse, fa-tooth, fa-baby',
    )
    short_description = models.CharField('Кратко', max_length=255)
    description = models.TextField('Подробное описание', blank=True)
    image = models.CharField(
        'Картинка (путь в static)', max_length=255, blank=True,
        help_text='Например: css/img/pre.jpg. Можно оставить пустым.',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('specialty_detail', args=[self.slug])


class Doctor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='doctor', verbose_name='Аккаунт врача',
        help_text='Аккаунт, через который врач входит в «Панель врача».',
    )
    name = models.CharField('ФИО', max_length=150)
    specialty = models.ForeignKey(
        Specialty, on_delete=models.PROTECT, related_name='doctors',
        verbose_name='Направление',
    )
    position = models.CharField(
        'Должность', max_length=150, blank=True,
        help_text='Например: «Врач-кардиолог высшей категории».',
    )
    experience = models.PositiveIntegerField('Стаж (лет)', default=0)
    education = models.TextField('Образование', blank=True)
    bio = models.TextField('О враче', blank=True)
    photo = models.ImageField('Фото', upload_to='doctors/', blank=True, null=True)
    price = models.PositiveIntegerField('Стоимость приёма (сом)', null=True, blank=True)
    slot_minutes = models.PositiveSmallIntegerField(
        'Длительность приёма (мин)', default=30,
        choices=[(15, '15 минут'), (20, '20 минут'), (30, '30 минут'), (45, '45 минут'), (60, '60 минут')],
    )
    is_active = models.BooleanField('Принимает пациентов', default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('doctors:detail', args=[self.pk])

    @property
    def title(self):
        return self.position or self.specialty.name

    @property
    def initials(self):
        parts = self.name.split()
        return ''.join(p[0] for p in parts[:2]).upper() or '?'

    @property
    def experience_label(self):
        n = self.experience
        if n % 10 == 1 and n % 100 != 11:
            word = 'год'
        elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            word = 'года'
        else:
            word = 'лет'
        return f'{n} {word}'


class WorkingHours(models.Model):
    """Рабочие часы врача в конкретный день недели."""

    WEEKDAYS = [
        (0, 'Понедельник'), (1, 'Вторник'), (2, 'Среда'), (3, 'Четверг'),
        (4, 'Пятница'), (5, 'Суббота'), (6, 'Воскресенье'),
    ]
    SHORT = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='working_hours', verbose_name='Врач')
    weekday = models.PositiveSmallIntegerField('День недели', choices=WEEKDAYS)
    start_time = models.TimeField('Начало')
    end_time = models.TimeField('Конец')

    class Meta:
        ordering = ['weekday', 'start_time']
        verbose_name = 'Рабочие часы'
        verbose_name_plural = 'График работы'
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'weekday'], name='unique_doctor_weekday'),
            models.CheckConstraint(condition=models.Q(end_time__gt=models.F('start_time')), name='working_hours_end_after_start'),
        ]

    def __str__(self):
        return f'{self.get_weekday_display()}: {self.start_time:%H:%M}–{self.end_time:%H:%M}'
