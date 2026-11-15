from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Profile(models.Model):

    class Gender(models.TextChoices):
        MALE = 'm', 'Мужской'
        FEMALE = 'f', 'Женский'

    class BloodType(models.TextChoices):
        O_POS = 'O+', 'I (O) Rh+'
        O_NEG = 'O-', 'I (O) Rh−'
        A_POS = 'A+', 'II (A) Rh+'
        A_NEG = 'A-', 'II (A) Rh−'
        B_POS = 'B+', 'III (B) Rh+'
        B_NEG = 'B-', 'III (B) Rh−'
        AB_POS = 'AB+', 'IV (AB) Rh+'
        AB_NEG = 'AB-', 'IV (AB) Rh−'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=30, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    gender = models.CharField('Пол', max_length=1, choices=Gender.choices, blank=True)
    blood_type = models.CharField('Группа крови', max_length=3, choices=BloodType.choices, blank=True)
    allergies = models.TextField('Аллергии', blank=True)
    chronic_conditions = models.TextField('Хронические заболевания', blank=True)

    class Meta:
        verbose_name = 'Медицинская карта'
        verbose_name_plural = 'Медицинские карты'

    def __str__(self):
        return f'Карта: {self.user.get_full_name() or self.user.username}'

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.localdate()
        b = self.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))
