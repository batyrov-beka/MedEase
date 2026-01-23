from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user','patient_name', 'patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date')
from django.contrib import admin

# Register your models here.
