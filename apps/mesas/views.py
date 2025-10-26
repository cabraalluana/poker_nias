import subprocess
import zipfile
import os

from django.shortcuts import get_object_or_404
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

def download_from_s3(file_list):
    """
    Baixa uma lista de arquivos do S3. Se um arquivo for .zip,
    ele é descompactado em uma pasta com o mesmo nome.
    """
    # Garante que a pasta de destino principal 'arquivos' exista
    if not os.path.exists("arquivos"):
        os.makedirs("arquivos")
        
    for file_name in file_list:
        s3_path = f"s3://fotografias-poker/static/{file_name}"
        local_destination_folder = "arquivos"
        
        print(f"Baixando '{file_name}' do S3...")
        
        # Executa o comando de download
        result = subprocess.run(["aws", "s3", "cp", s3_path, local_destination_folder], capture_output=True, text=True)
        
        # Verifica se o download foi bem-sucedido
        if result.returncode != 0:
            print(f"Erro ao baixar '{file_name}': {result.stderr}")
            continue # Pula para o próximo arquivo da lista

        print(f"'{file_name}' baixado com sucesso.")
        
        # --- LÓGICA DE DESCOMPACTAÇÃO ---
        
        # Constrói o caminho completo para o arquivo baixado
        local_file_path = os.path.join(local_destination_folder, file_name)
        
        # 1. Verifica se o arquivo termina com .zip
        if file_name.endswith('.zip'):
            print(f"Arquivo '{file_name}' é um zip. Descompactando...")
            
            # 2. Cria um nome para a pasta de destino (ex: 'meu_arquivo.zip' -> 'meu_arquivo')
            unzip_dir_name = os.path.splitext(file_name)[0]
            unzip_destination_path = os.path.join(local_destination_folder, unzip_dir_name)
            
            # Cria a pasta de destino se ela não existir
            os.makedirs(unzip_destination_path, exist_ok=True)
            
            try:
                # 3. Abre o arquivo .zip e extrai todo o conteúdo para a pasta de destino
                with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
                    zip_ref.extractall(unzip_destination_path)
                
                print(f"Descompactado com sucesso em: '{unzip_destination_path}'")
                
                # 4. (Opcional) Remove o arquivo .zip original após a descompactação
                # os.remove(local_file_path)
                # print(f"Arquivo '{file_name}' original removido.")
                
            except zipfile.BadZipFile:
                print(f"Erro: O arquivo '{file_name}' não é um arquivo zip válido ou está corrompido.")
            except Exception as e:
                print(f"Ocorreu um erro ao descompactar '{file_name}': {e}")
        
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
            # Se não estiver, retorna False
            return False

    # Se todos os códigos estiverem associados a uma mesa com status 1, retorna True
    return True