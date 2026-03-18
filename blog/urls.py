

from blog.views import base
from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='home'),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('categories/', views.categories, name='categories'),

]
