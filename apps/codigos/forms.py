from django import forms
from apps.codigos.models import Codigo
from datetime import datetime

class CodigoForms(forms.ModelForm):
    class Meta:
        model = Codigo
        exclude = ['usuario', ]  # Excluindo o campo 'idUsuario' do formulário
        labels = {
            'arquivo': 'Arquivo',
            'data_codigo': 'Data de envio'
        }
        widgets = {
            'arquivo': forms.FileInput(attrs={'class':'form-control'}),
        }
