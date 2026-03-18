# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('register/', views.register_view, name='register'),
#     path('login/', views.login_view, name='login'),
#     path('logout/', views.logout_view, name='logout'),
# ]


from django.urls import path
from .import views
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', views.profile, name='profile'),
path('verify/', views.verify_code_view, name='verify_code'),
path('resend-code/', views.resend_code_view, name='resend_code'),
]
