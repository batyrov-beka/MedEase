
# from django.conf.urls import url

from django.urls import path
from . import views


urlpatterns = [
    path('', views.patient_appointments, name='patient_appointments'),
    path('', views.patient_dashboard, name='patient_dashboard'),
]