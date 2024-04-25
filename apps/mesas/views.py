from django.shortcuts import render
from django.apps import apps
from apps.codigos.models import Codigo
from django.db import transaction
from apps.mesas.models import Mesa, Codigo_Mesa
from django.contrib.auth.models import User
from django.db.models import F

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