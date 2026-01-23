from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'experience')
    search_fields = ('name', 'specialty')
from django.contrib import admin

# Register your models here.
