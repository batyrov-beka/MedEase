from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request , 'index.html'),

def base (request):
    return render(request , 'base.html')


def about(request):
    return render(request , 'about.html')

def contact(request):
    return render(request , 'contact.html')

def categories(request):
    return render(request , 'categories.html')