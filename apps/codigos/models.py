from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Codigo(models.Model):
    arquivo = models.FileField(upload_to="arquivos", blank=False)
    usuario = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    data_codigo = models.DateField(default=date.today(), blank=False)

def __str__(self):
    return f"Código de {self.usuario.username}: {self.arquivo.name}"