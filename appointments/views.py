from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor
from .models import Appointment

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        username = request.POST.get('text')
        name = request.POST.get('text-conf')
        date = request.POST['date']
        time = request.POST['time']

        Appointment.objects.create(
            user=request.user,
            doctor=doctor,
            patient=username,
            patient_name=name,
            date=date,
            time=time,

        )
        return redirect('profile')

    return render(request, 'book_appointment.html', {'doctor': doctor})





@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'my_appointments.html', {
        'appointments': appointments
    })


@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        user=request.user
    )
    appointment.delete()
    return redirect('appointments:my')