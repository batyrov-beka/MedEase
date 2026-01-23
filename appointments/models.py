from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=255, null=True, blank=True)
    patient = models.CharField(max_length=250, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"{self.user.username} → {self.doctor.name} ({self.date} {self.time})"
from django.db import models

# Create your models here.
