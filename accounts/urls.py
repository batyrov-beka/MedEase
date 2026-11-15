from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify/', views.verify_code_view, name='verify_code'),
    path('resend-code/', views.resend_code_view, name='resend_code'),
    path('login/', views.MedLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Смена пароля
    path('password/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url=reverse_lazy('password_change_done'),
    ), name='password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html',
    ), name='password_change_done'),

    # Восстановление пароля по email
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.txt',
        subject_template_name='accounts/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
]
