from django.db import models
from apps.mesas.models import Mesa

class Resultados(models.Model):
    arquivoResultado = models.FileField(upload_to="resultados", blank=False)
    mesa = models.ForeignKey(Mesa, default=None, on_delete=models.CASCADE)

def __str__(self):
    return f"Resultados da mesa {self.mesa.id} salvos com sucesso."