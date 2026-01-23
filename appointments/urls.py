# from django.conf.urls import url
from django.urls import include, path
from . import views

app_name = 'appointments'

urlpatterns = [

    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my/', views.my_appointments, name='my'),
    path('delete/<int:appointment_id>/', views.delete_appointment, name='delete'),

]