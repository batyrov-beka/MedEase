
from django.shortcuts import render, get_object_or_404
from .models import Doctor
from appointments.models import Appointment
# Create your views here.
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})



def doctor_detail(request, id):
    doctor = get_object_or_404(Doctor,id=id)
    return render(request, 'detail.html',{'doctor':doctor})



def dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by('date', 'time')

    return render(request, 'dashboard.html', {
        'doctor': doctor,
        'appointments': appointments
    })
