from django import forms

from .models import Appointment
from .services import booking_window, get_free_times


class BookingForm(forms.Form):
    date = forms.DateField(widget=forms.HiddenInput)
    time = forms.TimeField(widget=forms.HiddenInput, error_messages={'required': 'Выберите время приёма.'})
    patient_name = forms.CharField(label='ФИО пациента', max_length=255)
    phone = forms.CharField(label='Телефон', max_length=30)
    reason = forms.CharField(
        label='Жалобы / причина обращения', required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Кратко опишите, что беспокоит (необязательно)'}),
    )

    def __init__(self, *args, doctor=None, **kwargs):
        self.doctor = doctor
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update({'placeholder': '+996 ___ ___ ___', 'inputmode': 'tel'})

    def clean(self):
        data = super().clean()
        day, time = data.get('date'), data.get('time')
        if not day or not time:
            return data
        start, end = booking_window()
        if not start <= day <= end:
            raise forms.ValidationError('На эту дату запись недоступна.')
        if time not in get_free_times(self.doctor, day):
            raise forms.ValidationError('Это время уже занято или недоступно. Выберите другое.')
        return data


class DoctorNotesForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor_notes']
        widgets = {
            'doctor_notes': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Диагноз, назначения, рекомендации, дата повторного визита…',
            }),
        }
