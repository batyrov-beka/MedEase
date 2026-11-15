from django.urls import path

from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/<int:doctor_id>/', views.book_appointment, name='book'),
    path('my/', views.my_appointments, name='my'),
    path('<int:pk>/', views.appointment_detail, name='detail'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
    path('<int:pk>/status/', views.set_status, name='status'),
]
