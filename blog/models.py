from django.db import models

# Create your models here.
from django.contrib.auth.models import User



class Women(models.Model):
    name = models.CharField( max_length=100,verbose_name="Имя"
    )
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(
        verbose_name="Сообщение"
    )
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



