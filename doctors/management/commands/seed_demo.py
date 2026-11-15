import datetime

from django.core.management.base import BaseCommand

from doctors.models import Doctor, Specialty, WorkingHours

WEEKDAY_HOURS = (datetime.time(9, 0), datetime.time(17, 0))
SATURDAY_HOURS = (datetime.time(9, 0), datetime.time(14, 0))


class Command(BaseCommand):
    help = (
        'Готовит базу к работе: добавляет график работы врачам без графика '
        '(Пн–Пт 9:00–17:00, Сб 9:00–14:00) и убирает текст-заглушку «Lorem ipsum».'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--assign-specialties', action='store_true',
            help='Распределить врачей-«терапевтов» по разным направлениям (для демонстрации).',
        )

    def handle(self, *args, assign_specialties=False, **options):
        hours_added = cleaned = reassigned = 0

        for doctor in Doctor.objects.all():
            if not doctor.working_hours.exists():
                for weekday in range(5):
                    WorkingHours.objects.create(doctor=doctor, weekday=weekday,
                                                start_time=WEEKDAY_HOURS[0], end_time=WEEKDAY_HOURS[1])
                WorkingHours.objects.create(doctor=doctor, weekday=5,
                                            start_time=SATURDAY_HOURS[0], end_time=SATURDAY_HOURS[1])
                hours_added += 1

            changed = []
            if 'lorem ipsum' in doctor.bio.lower():
                doctor.bio = ''
                changed.append('bio')
            if doctor.position.strip().lower() in {'врач', 'медик'}:
                doctor.position = ''
                changed.append('position')
            if changed:
                doctor.save(update_fields=changed)
                cleaned += 1

        if assign_specialties:
            specialties = list(Specialty.objects.filter(is_active=True).exclude(slug='terapevt'))
            therapists = Doctor.objects.filter(specialty__slug='terapevt').order_by('pk')
            # Одного оставляем терапевтом, остальных распределяем
            for doctor, specialty in zip(therapists[1:], specialties):
                doctor.specialty = specialty
                doctor.save(update_fields=['specialty'])
                reassigned += 1

        self.stdout.write(self.style.SUCCESS(
            f'График добавлен врачам: {hours_added}. Очищено карточек: {cleaned}. '
            f'Переназначено направлений: {reassigned}.'
        ))
