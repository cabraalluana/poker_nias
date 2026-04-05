from rest_framework import serializers
from apps.mesas.models import Torneio, ResultadoTorneio

class ResultadoSerializer(serializers.ModelSerializer):
    # Pega o username do dono do bot vinculado ao código
    nome_jogador = serializers.CharField(source='codigo.usuario.username', read_only=True)

    class Meta:
        model = ResultadoTorneio
        fields = ['posicao', 'nome_jogador', 'fichas_finais']

class TorneioSerializer(serializers.ModelSerializer):
    rankings = ResultadoSerializer(many=True, read_only=True)

    class Meta:
        model = Torneio
        fields = ['id', 'data_inicio', 'quantidade_jogadores', 'tempo_total_ms', 'rankings']