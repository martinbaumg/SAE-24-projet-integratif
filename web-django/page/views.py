from django.shortcuts import render
from .models import SensorsData

# Create your views here.

def index(request):
    temp = SensorsData.objects.all()
    return render(request, 'index.html', {'temp': temp})