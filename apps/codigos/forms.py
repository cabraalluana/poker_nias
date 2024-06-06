from django import forms
from apps.codigos.models import Codigo

class CodigoForms(forms.ModelForm):
    class Meta:
        model = Codigo
        exclude = ['usuario', ]  # Excluindo o campo 'idUsuario' do formulário
        labels = {
            'arquivo': 'Arquivo',
        }
        widgets = {
            'arquivo': forms.FileInput(attrs={'class':'form-control'}),
        }
