import subprocess
import zipfile
import os
import boto3
import sys

from django.shortcuts import get_object_or_404
from django.apps import apps
from apps.codigos.models import Codigo
from django.db import transaction
from apps.mesas.models import Mesa, Codigo_Mesa
from django.contrib.auth.models import User
from django.db.models import F
from botocore.exceptions import ClientError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.mesas.models import Torneio
from .serializers import TorneioSerializer

for model in apps.get_models():
    total_registros = model.objects.count()
    print(f"{model._meta.verbose_name_plural}: {total_registros}")
    
def numeroJogadores():
    """
    Esta função retorna o número de jogadores que enviaram códigos
    :return: Número de jogadores
    """
    
    return Codigo.objects.count()

def get_codigo_ids():
    """
    Esta função retorna uma lista de IDs dos códigos enviados
    :return: Lista de IDs dos códigos
    """
    
    # Consulte todos os registros do modelo Codigo e pegue os IDs
    codigos = Codigo.objects.all()
    
    # Crie uma lista de IDs
    codigo_ids = [codigo.id for codigo in codigos]
    
    return codigo_ids

def criar_mesa_e_vincular_codigos(listas_de_codigos):
    """
        Esta função cria novas mesas com status "ativo" e vincula códigos específicos a essas mesas.

        :para listas_de_codigos: Uma lista de listas contendo IDs dos códigos a serem vinculados a cada mesa.
                                Cada lista interna contém os IDs dos códigos que serão vinculados a uma mesa específica.
                                Exemplo: [[1, 2, 3], [4, 5]] indica que a primeira mesa terá os códigos com IDs 1, 2 e 3,
                                enquanto a segunda mesa terá os códigos com IDs 4 e 5.
        :return: A função não retorna nada, mas imprime uma mensagem indicando se as mesas e códigos foram vinculados com sucesso
                ou exibe uma mensagem de erro em caso de falha.
    """
    
    try:
        with transaction.atomic():  # Inicia uma transação
            for lista_de_codigos in listas_de_codigos:
                # Cria uma nova mesa com status "ativo"
                mesa = Mesa.objects.create(status='1')
                
                # Vincula os códigos à mesa na tabela CODIGO_MESA
                for codigo in lista_de_codigos:
                    Codigo_Mesa.objects.create(mesa_id=mesa.id, codigo_id=codigo)
        
        print("Mesas e códigos vinculados com sucesso.")
        
    except Exception as e:
        # Em caso de erro, desfaz as alterações
        print(f"Erro ao criar mesas e vincular códigos: {e}")

def obter_id_mesas(status):
    # Consulta as mesas com o status fornecido usando o ORM do Django
    mesas = Mesa.objects.filter(status=status)

    # Obtém os IDs das mesas
    id_mesas = [mesa.id for mesa in mesas]

    return id_mesas

def consultar_mesas_e_codigos(id_mesas):
    resultado = []
    
    try:
        for id_mesa in id_mesas:
            # Consultar os dados desejados usando o ORM do Django
            dados_mesa = (
                Mesa.objects
                .filter(id=id_mesa)
                .values(
                    idMesa=F('id'),  # renomeia o campo para idMesa
                    idCodigo=F('codigo_mesa__codigo__id'),  # id do código
                    user=F('codigo_mesa__codigo__usuario__username')  # nome do usuário
                )
            )
            
            resultado.append(list(dados_mesa))

        return resultado

    except Exception as e:
        return [f"Erro ao consultar mesa {id_mesa}: {e}"]
    
    
def criar_pastas_mesas_ativas():    
    try:
        # Consulta para selecionar idMesa em que status = status fornecido
        id_mesas = Mesa.objects.filter(status=True).values_list('id', flat=True)
        
        return list(id_mesas)

    except Exception as e:
        print(f"Erro ao obter idMesas com status {True}: {e}")
        return []
    
def consultar_arquivo_e_id_mesas():
    try:
        # Consulta usando ORM do Django para obter o nome do arquivo e o id da mesa
        resultados = (
            Codigo.objects
            .filter(codigo_mesa__mesa__status=1)  # Filtra os códigos associados a mesas ativas
            .values_list('arquivo', 'codigo_mesa__mesa_id')  # Seleciona o nome do arquivo e o id da mesa
        )

        # Converte o resultado em uma lista de tuplas (idMesa, arquivo)
        lista_id_arquivo = list(resultados)

        return lista_id_arquivo

    except Exception as e:
        print(f"Erro ao consultar arquivo e idMesas: {e}")
        return []

def download_unico_e_extrair(arquivo_nome, pasta_destino):
    """
    BAIXA DO S3 E RETORNA O CAMINHO PARA O READ.PY
    """
    import os, boto3, zipfile
    
    s3 = boto3.client('s3')
    bucket_name = 'fotografias-poker'
    s3_folder = 'static/arquivos/' 
    print(arquivo_nome)
    
    file_name = os.path.basename(arquivo_nome) 
    s3_key = f"{s3_folder}{file_name}"
    print(s3_key)
    local_path = os.path.join(pasta_destino, file_name)

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    try:
        print(f"📥 Baixando '{file_name}' para '{pasta_destino}'...")
        s3.download_file(bucket_name, s3_key, local_path)
        
        # Se for ZIP, extrai e retorna o caminho do bot lá dentro
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(local_path, 'r') as zip_ref:
                zip_ref.extractall(pasta_destino)
            os.remove(local_path)
            return os.path.join(pasta_destino, 'bot.py') 

        # --- O PONTO CRÍTICO: ADICIONE ESTA LINHA ---
        # Se for um arquivo .py, precisamos retornar o caminho dele!
        return local_path 

    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return None
        
def alterar_status_mesa(id_mesa):
    try:
        # Buscar a mesa pelo ID
        mesa = Mesa.objects.get(id=id_mesa)
        
        # Atualizar o status da mesa
        mesa.status = 0
        mesa.save()
        
        return True  # Retorna True se a atualização for bem-sucedida
    except Mesa.DoesNotExist:
        return f"Mesa com id {id_mesa} não encontrada"
    except Exception as e:
        return f"Erro ao atualizar o status da mesa: {e}"
    
def verificar_codigos():
    # Obtém todos os códigos
    codigos = Codigo.objects.all()

    for codigo in codigos:
        # Verifica se o código está associado a alguma mesa com status 1
        if not Codigo_Mesa.objects.filter(codigo=codigo, mesa__status=True).exists():
            # SE NÃO ESTIVER EM MESA ATIVA, significa que temos trabalho!
            return True

    # Se todos já estiverem em mesas ativas, não há nada a fazer
    return False

class UltimoTorneioAPI(APIView):
    """Retorna o status e ranking do torneio mais recente"""
    def get(self, request):
        torneio = Torneio.objects.last()
        if not torneio:
            return Response({"erro": "Nenhum torneio realizado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TorneioSerializer(torneio)
        return Response(serializer.data)

class DispararTorneioAPI(APIView):
    """Gatilho para iniciar o read.py via requisição POST"""
    def post(self, request):
        try:
            # sys.executable garante que usamos o Python do ambiente virtual/docker
            subprocess.Popen([sys.executable, "read.py"])
            return Response({"mensagem": "🚀 Torneio iniciado em segundo plano!"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"erro": f"Falha ao iniciar: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)