import datetime
import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from doctors.models import Doctor, Specialty, WorkingHours

from .models import Appointment
from .services import get_slots


def next_weekday(weekday):
    """Ближайшая будущая дата с заданным днём недели (не сегодня)."""
    day = timezone.localdate() + datetime.timedelta(days=1)
    while day.weekday() != weekday:
        day += datetime.timedelta(days=1)
    return day


class BaseCase(TestCase):
    def setUp(self):
        self.specialty = Specialty.objects.get(slug='kardiolog')
        self.doctor_user = User.objects.create_user('doc', password='Pass-12345')
        self.doctor = Doctor.objects.create(name='Иванов Иван', specialty=self.specialty,
                                            user=self.doctor_user, slot_minutes=30)
        WorkingHours.objects.create(doctor=self.doctor, weekday=0,
                                    start_time=datetime.time(9), end_time=datetime.time(11))
        self.patient = User.objects.create_user('patient', email='p@example.com', password='Pass-12345')
        self.monday = next_weekday(0)


class SlotTests(BaseCase):
    def test_slots_follow_working_hours(self):
        slots = get_slots(self.doctor, self.monday)
        self.assertEqual([s['time'].strftime('%H:%M') for s in slots], ['09:00', '09:30', '10:00', '10:30'])
        self.assertTrue(all(s['free'] for s in slots))

    def test_no_slots_on_day_off(self):
        self.assertEqual(get_slots(self.doctor, next_weekday(2)), [])

    def test_taken_slot_is_not_free_but_cancelled_is(self):
        Appointment.objects.create(user=self.patient, doctor=self.doctor, patient_name='A',
                                   date=self.monday, time=datetime.time(9, 30))
        Appointment.objects.create(user=self.patient, doctor=self.doctor, patient_name='B',
                                   date=self.monday, time=datetime.time(10),
                                   status=Appointment.Status.CANCELLED)
        free = {s['time'] for s in get_slots(self.doctor, self.monday) if s['free']}
        self.assertNotIn(datetime.time(9, 30), free)
        self.assertIn(datetime.time(10), free)


class BookingTests(BaseCase):
    def book(self, time='09:00', date=None):
        return self.client.post(reverse('appointments:book', args=[self.doctor.pk]), {
            'date': (date or self.monday).isoformat(), 'time': time,
            'patient_name': 'Пациент Тестов', 'phone': '+996 555 000 000', 'reason': 'Болит сердце',
        })

    def test_requires_login(self):
        resp = self.client.get(reverse('appointments:book', args=[self.doctor.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_booking_creates_appointment_and_sends_email(self):
        self.client.login(username='patient', password='Pass-12345')
        resp = self.book()
        a = Appointment.objects.get()
        self.assertRedirects(resp, a.get_absolute_url())
        self.assertEqual(a.status, Appointment.Status.PENDING)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(self.patient.profile.phone, '+996 555 000 000')

    def test_cannot_double_book_slot(self):
        self.client.login(username='patient', password='Pass-12345')
        self.book()
        resp = self.book()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_cannot_book_outside_hours(self):
        self.client.login(username='patient', password='Pass-12345')
        self.book(time='15:00')
        self.book(time='09:00', date=next_weekday(2))
        self.assertEqual(Appointment.objects.count(), 0)


class AccessTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.appt = Appointment.objects.create(user=self.patient, doctor=self.doctor, patient_name='P',
                                               date=self.monday, time=datetime.time(9))
        User.objects.create_user('stranger', password='Pass-12345')

    def test_stranger_cannot_see_or_cancel(self):
        self.client.login(username='stranger', password='Pass-12345')
        self.assertEqual(self.client.get(self.appt.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.post(reverse('appointments:cancel', args=[self.appt.pk])).status_code, 404)

    def test_patient_can_cancel(self):
        self.client.login(username='patient', password='Pass-12345')
        self.client.post(reverse('appointments:cancel', args=[self.appt.pk]))
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, Appointment.Status.CANCELLED)

    def test_patient_cannot_change_status(self):
        self.client.login(username='patient', password='Pass-12345')
        resp = self.client.post(reverse('appointments:status', args=[self.appt.pk]), {'status': 'completed'})
        self.assertEqual(resp.status_code, 404)

    def test_doctor_confirms_and_writes_notes(self):
        self.client.login(username='doc', password='Pass-12345')
        self.assertEqual(self.client.get(reverse('doctors:dashboard')).status_code, 200)
        self.client.post(reverse('appointments:status', args=[self.appt.pk]), {'status': 'confirmed'})
        self.client.post(self.appt.get_absolute_url(), {'doctor_notes': 'Здоров', 'complete': '1'})
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, Appointment.Status.COMPLETED)
        self.assertEqual(self.appt.doctor_notes, 'Здоров')

    def test_dashboard_only_for_doctors(self):
        self.client.login(username='patient', password='Pass-12345')
        self.assertEqual(self.client.get(reverse('doctors:dashboard')).status_code, 404)


class RegistrationTests(TestCase):
    def test_full_registration_flow_sets_working_password(self):
        resp = self.client.post(reverse('register'), {
            'first_name': 'Айбек', 'last_name': 'Асанов', 'username': 'aibek',
            'email': 'aibek@example.com', 'phone': '+996700000000',
            'password1': 'Strong-pass-77', 'password2': 'Strong-pass-77',
        })
        self.assertRedirects(resp, reverse('verify_code'))
        code = re.search(r'\b(\d{6})\b', mail.outbox[0].body).group(1)

        resp = self.client.post(reverse('verify_code'), {'code': '000000' if code != '000000' else '111111'})
        self.assertContains(resp, 'Неверный код')

        resp = self.client.post(reverse('verify_code'), {'code': code})
        self.assertRedirects(resp, reverse('profile'))
        user = User.objects.get(username='aibek')
        self.assertTrue(user.check_password('Strong-pass-77'))
        self.assertEqual(user.profile.phone, '+996700000000')

        self.client.logout()
        self.assertTrue(self.client.login(username='aibek', password='Strong-pass-77'))

    def test_login_by_email(self):
        User.objects.create_user('nurlan', email='nurlan@example.com', password='Strong-pass-77')
        resp = self.client.post(reverse('login'), {'username': 'nurlan@example.com', 'password': 'Strong-pass-77'})
        self.assertRedirects(resp, reverse('profile'))


class PublicPagesTests(BaseCase):
    def test_public_pages_open(self):
        urls = [
            reverse('home'), reverse('services'), reverse('specialty_detail', args=['kardiolog']),
            reverse('schedule'), reverse('contact'), reverse('doctors:list'),
            reverse('doctors:detail', args=[self.doctor.pk]), reverse('login'), reverse('register'),
            reverse('doctors:list') + '?q=Иван&specialty=kardiolog',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_logged_in_pages_open(self):
        self.client.login(username='patient', password='Pass-12345')
        for url in [reverse('profile'), reverse('profile_edit'), reverse('appointments:my'),
                    reverse('appointments:book', args=[self.doctor.pk]), reverse('password_change')]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_contact_form_saves_request(self):
        from blog.models import ContactRequest
        self.client.post(reverse('contact'), {'name': 'Аида', 'phone': '+996555', 'message': 'Вопрос'})
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_old_urls_redirect(self):
        self.assertRedirects(self.client.get('/about/'), reverse('schedule'), status_code=301)
        self.assertRedirects(self.client.get('/categories/'), reverse('services'), status_code=301)
