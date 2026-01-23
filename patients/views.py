from django.shortcuts import render
# from .models import patients
# Create your views here.
def patient_appointments(request):
    return render(request, 'patient_appointments.html')

def patient_dashboard(request):
    return render(request, 'patient_dashboard.html')
