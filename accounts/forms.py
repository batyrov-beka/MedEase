from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    email = forms.EmailField(label='Электронная почта', help_text='На неё придёт код подтверждения.')
    phone = forms.CharField(label='Телефон', max_length=30, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']
        labels = {'username': 'Логин'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Латинские буквы, цифры и символы @/./+/-/_'
        self.fields['password1'].help_text = 'Не менее 8 символов, не только цифры.'
        self.fields['phone'].widget.attrs.update({'placeholder': '+996 ___ ___ ___', 'inputmode': 'tel'})

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с такой почтой уже зарегистрирован.')
        return email


class LoginForm(AuthenticationForm):

    username = forms.CharField(label='Логин или email', max_length=254,
                               widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}))

    def clean(self):
        login = self.cleaned_data.get('username', '')
        if '@' in login:
            user = User.objects.filter(email__iexact=login).order_by('-last_login').first()
            if user:
                self.cleaned_data['username'] = user.username
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверный логин или пароль.', code='invalid_login')
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'birth_date', 'gender', 'blood_type', 'allergies', 'chronic_conditions']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'allergies': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Например: пенициллин, орехи. Если нет — оставьте пустым.'}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Например: гипертония, диабет 2 типа.'}),
        }
