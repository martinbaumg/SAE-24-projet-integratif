
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, HttpResponseRedirect,HttpResponse
from django.http import Http404,FileResponse
from .models import Sensors, SensorsData
import mimetypes
from django.contrib import admin
from .forms import SensorsForm
from . import models


# Create your views here.

def index(request): 
    sensors = Sensors.objects.all()
    sensorsdata = SensorsData.objects.all()
    return render(request, 'index.html', {'sensors': sensors, 'sensorsdata': sensorsdata})


def edit(request, sensors_id):
    sensors = get_object_or_404(models.Sensors, pk=sensors_id)
    if request.method == 'POST':
        form = SensorsForm(request.POST, instance=sensors)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = SensorsForm(instance=sensors)
    return render(request, 'editname.html', {'form': form})

def delete(request, id):
    temp = SensorsData.objects.all()
    sensors = models.SensorsData.objects.get(id=id)
    sensors.delete()
    return render(request, 'index.html', {'temp': temp})

def temp(request, id):
    temp = SensorsData.objects.filter(sensor__id=id)
    return render(request, 'data.html', {'temp': temp})