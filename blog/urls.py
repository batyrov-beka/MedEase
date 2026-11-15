from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.specialty_detail, name='specialty_detail'),
    path('schedule/', views.schedule, name='schedule'),
    path('contact/', views.contact, name='contact'),

    # Старые адреса — перенаправляем, чтобы ссылки не ломались
    path('about/', RedirectView.as_view(pattern_name='schedule', permanent=True)),
    path('categories/', RedirectView.as_view(pattern_name='services', permanent=True)),
]
