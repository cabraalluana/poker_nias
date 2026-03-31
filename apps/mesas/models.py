from django.db import models
from apps.codigos.models import Codigo

class Mesa(models.Model):
    status = models.BooleanField(default=True)
    # Adicionado campo para vincular a um torneio específico
    torneio = models.ForeignKey('Torneio', on_delete=models.CASCADE, null=True, blank=True)

class Codigo_Mesa(models.Model):
    codigo = models.ForeignKey(Codigo, default=None, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, default=None, on_delete=models.CASCADE)

class Torneio(models.Model):
    """Agrupa todas as fases de uma execução do read.py"""
    data_inicio = models.DateTimeField(auto_now_add=True)
    tempo_total_ms = models.IntegerField(null=True, blank=True) # Telemetria Global
    quantidade_jogadores = models.IntegerField(default=0)

    def __str__(self):
        return f"Torneio {self.id} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"

class ResultadoTorneio(models.Model):
    """O Ranking Definitivo (O que aparece no final do funil)"""
    torneio = models.ForeignKey(Torneio, on_delete=models.CASCADE, related_name='rankings')
    codigo = models.ForeignKey(Codigo, on_delete=models.CASCADE)
    posicao = models.IntegerField()
    fichas_finais = models.FloatField()

    class Meta:
        ordering = ['posicao']

class HistoricoPartida(models.Model):
    """Dados de cada mesa individual (Telemetria de Fase e Replay)"""
    torneio = models.ForeignKey(Torneio, on_delete=models.CASCADE, related_name='partidas')
    mesa_id_original = models.IntegerField()
    log_arquivo = models.CharField(max_length=255) # Caminho S3/Local do log_acoes.txt
    tempo_processamento_ms = models.IntegerField() # Telemetria da Mesa
    fase = models.IntegerField(default=1)

    def __str__(self):
        return f"Mesa {self.mesa_id_original} - Fase {self.fase}"