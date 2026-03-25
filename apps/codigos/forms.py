from django import forms
from apps.codigos.models import Codigo

class CodigoForms(forms.ModelForm):
    class Meta:
        model = Codigo
        exclude = ['usuario', ]
        labels = {
            'arquivo': 'Arquivo (.zip com main.m)', # Instrução clara
        }
        widgets = {
            'arquivo': forms.FileInput(attrs={'class':'form-control', 'accept': '.zip'}), # Filtro visual
        }
