from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя')
    email = forms.EmailField(label='Электронная почта', required=True)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
#
#
# class RegisterForm(UserCreationForm):
#     username = forms.CharField(label='Имя пользователя')
#     email = forms.EmailField(label='Электронная почта', required=True)
#     password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Подтвердите Пароль', widget=forms.PasswordInput)
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2')
