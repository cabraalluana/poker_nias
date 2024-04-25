from django import forms
from apps.codigos.models import Codigo
from datetime import datetime

class CodigoForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_codigo'].initial = datetime.now().strftime('%Y-%m-%d')

    class Meta:
        model = Codigo
        exclude = ['usuario', ]  # Excluindo o campo 'idUsuario' do formulário
        labels = {
            'arquivo': 'Arquivo',
            'data_codigo': 'Data de envio'
        }
        widgets = {
            'arquivo': forms.FileInput(attrs={'class':'form-control'}),
            'data_codigo': forms.DateInput(
                format='%d/%m/%Y',
                attrs={
                    'type':'date',
                    'class':'form-control'
                    }
                )
        }
