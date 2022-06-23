from .models import SensorsData, Sensors
from django import forms
from . import models
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _


class SensorsForm(ModelForm):
    class Meta:
        model = Sensors
        fields = ['emplacement', 'nom', 'piece']
        label = {
            'nom': 'Nom du capteur',
            'emplacement': 'Emplacement',
            'piece': 'Pièce',
        }

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'emplacement': forms.TextInput(attrs={'class': 'form-control'}),

        }