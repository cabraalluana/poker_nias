from django.db import models
from apps.codigos.models import Codigo

class Mesa(models.Model):
    status = models.BooleanField(default=True)
    
class Codigo_Mesa(models.Model):
    codigo = models.ForeignKey(Codigo, default=None, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, default=None, on_delete=models.CASCADE)
    
def __str__(self):
    return f"Mesa {self.id} salva com sucesso"