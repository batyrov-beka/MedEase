# from main.urls import urlpatterns
from django.urls import path
from . import views

app_name = 'doctors'
urlpatterns = [

    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:id>/', views.doctor_detail, name='detail'),

    path('dashboard/', views.dashboard, name='dashboard'),
]
























