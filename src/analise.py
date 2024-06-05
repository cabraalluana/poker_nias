import math
import random
import os
import shutil
import zipfile

from apps.mesas import views
from prettytable import PrettyTable

def numeroJogadores():
    """
    Esta função retorna o número de jogadores que enviaram códigos
    :return: Número de jogadores
    """
    
    return views.numeroJogadores()

def get_codigo_ids():
    """
    Esta função retorna uma lista de IDs dos códigos enviados
    :return: Lista de IDs dos códigos
    """
    
    return views.get_codigo_ids()

def encontrar_n(num_jogadores):
    """
    Esta função encontra o valor de 'n' para distribuir jogadores em mesas de forma equilibrada
    :param num_jogadores: Número total de jogadores
    :return: O valor de 'n' encontrado ou None se não for possível dividir equilibradamente
    """
    if num_jogadores <= 10:
        return 1
    elif num_jogadores % 10 == 0:
        return int(num_jogadores / 10)
    else:
        for n in range(2, num_jogadores):
            if (num_jogadores / n) > 3 and (num_jogadores/n) <= 10:
                return n
    return None

def numeroJogadoresMesa(numero_jogadores):
    """
    Esta função distribui os jogadores em mesas de forma equilibrada
    :param numero_jogadores: Número total de jogadores
    :return: Lista com a quantidade de jogadores em cada mesa
    """
    n = encontrar_n(numero_jogadores)
    jogadoresRestantes = numero_jogadores

    while jogadoresRestantes > numero_jogadores % n:
        qtdJogadoresMesas = []

        for i in range(n):
            qtdJogadoresMesas.append(math.floor(numero_jogadores / n))
            jogadoresRestantes = jogadoresRestantes - qtdJogadoresMesas[i]

    sobra = jogadoresRestantes
    for i in range(0, sobra):
        qtdJogadoresMesas[i] = qtdJogadoresMesas[i] + 1
        jogadoresRestantes = jogadoresRestantes - 1

    print("="*100)
    print("mesa\tQuantidade de jogadores")
    for i in range(len(qtdJogadoresMesas)):
        print(f"{i + 1}\t{qtdJogadoresMesas[i]}")

    return qtdJogadoresMesas

def sortear_mesas(num_jogadores, listaIDs):
    """
    Esta função distribui jogadores aleatoriamente em mesas e exibe a distribuição
    :param num_jogadores: Número total de jogadores
    :param listaIDs: Lista de IDs de jogadores
    :return: Lista de listas contendo os idCodigo em cada mesa
    """
    num_jogadores_por_mesa = numeroJogadoresMesa(num_jogadores)
    num_mesas = len(num_jogadores_por_mesa)

    random.shuffle(listaIDs)

    tabela = {}
    indice_jogador = 0
    id_codigos_mesas = []  # Lista para armazenar os idCodigo em cada mesa

    for mesa in range(1, num_mesas + 1):
        num_jogadores = num_jogadores_por_mesa[mesa - 1]
        jogadores_na_mesa = []

        for _ in range(num_jogadores):
            jogadores_na_mesa.append(listaIDs[indice_jogador])
            id_codigos_mesas.append(listaIDs[indice_jogador])  # Adiciona o idCodigo à lista
            indice_jogador += 1

        tabela[mesa] = jogadores_na_mesa

    print("="*100)
    print("mesa\tjogadores")
    for mesa, jogadores_na_mesa in tabela.items():
        print(f"{mesa}\t{jogadores_na_mesa}")

    # Retornar o vetor com as linhas da coluna 2 da tabela
    return [jogadores_na_mesa for jogadores_na_mesa in tabela.values()]

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
    
    views.criar_mesa_e_vincular_codigos(listas_de_codigos)
    
def obter_id_mesas(status):
    return views.obter_id_mesas(status)

def consultar_mesas_e_codigos(id_mesas, status):
     # Verificar se id_mesas não é uma lista vazia
    if not id_mesas:
        if status:
            print("Não existe nenhuma mesa ativa no momento")
        else:
            print("Não existe nenhuma mesa inativa no momento")
        return

    # Criar uma tabela
    tabela = PrettyTable()

    # Definir os nomes das colunas da tabela
    tabela.field_names = ["idMesa", "idCodigo", "user"]

    # Obter os dados do banco de dados usando a função bdMesas.consultar_mesas_e_codigos
    for tupla in views.consultar_mesas_e_codigos(id_mesas):
        # Iterar sobre os resultados da consulta
        for resultado in tupla:
            # Adicionar uma linha à tabela para cada resultado
            tabela.add_row([resultado['idMesa'], resultado['idCodigo'], resultado['user']])

    # Imprimir a tabela formatada
    print(tabela)
    
def criar_pastas_mesas_ativas():
    caminho_pasta = 'mesas_ativas'
    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)
    else:
        # Itera sobre todos os arquivos na pasta
        for arquivo in os.listdir(caminho_pasta):
            try:
                # Monta o caminho completo do arquivo
                caminho_arquivo = os.path.join(caminho_pasta, arquivo)
                # Verifica se é um arquivo e não um diretório
                if os.path.isfile(caminho_arquivo):
                    # Remove o arquivo
                    os.unlink(caminho_arquivo)
                # Se for um diretório, remove recursivamente
                elif os.path.isdir(caminho_arquivo):
                    shutil.rmtree(caminho_arquivo)
            except Exception as e:
                print(f"Erro ao apagar {caminho_arquivo}: {e}")

    listaIdMesa = views.criar_pastas_mesas_ativas()
    
    # Iterar sobre os resultados
    for idMesa in listaIdMesa:
        # Criar o nome da pasta
        nome_pasta = f'mesa_{idMesa}'
            
        # Caminho completo da pasta
        caminho_completo = os.path.join(caminho_pasta, nome_pasta)
            
        # Verificar se a pasta não existe antes de criar
        if not os.path.exists(caminho_completo):
            os.makedirs(caminho_completo)
            
    return listaIdMesa

def consultar_arquivo_e_id_mesas():
    return views.consultar_arquivo_e_id_mesas()

def download_from_s3(file_list):
    views.download_from_s3(file_list)
    
def dividir_codigo_mesas(lista_arquivos):
    # Percorre a lista de arquivos
    for nome_arquivo, id_mesa in lista_arquivos:
        # Diretório de origem do arquivo
        origem = nome_arquivo
        # Diretório de destino da mesa
        destino = f"mesas_ativas/mesa_{id_mesa}"
        
        # Verifica se o diretório de destino existe, se não, cria-o
        if not os.path.exists(destino):
            os.makedirs(destino)
        
        # Verifica se o arquivo é um arquivo ZIP
        if nome_arquivo.endswith('.zip'):
            # Extrai o conteúdo do arquivo ZIP
            with zipfile.ZipFile(origem, 'r') as zip_ref:
                zip_ref.extractall(destino)
        else:
            # Move o arquivo para o diretório de destino
            shutil.move(origem, destino)
        
def alterar_status_mesa(id_mesa):
    views.alterar_status_mesa(id_mesa)
    
def mover_arquivos(id_mesa):
    # Definindo os caminhos das pastas
    pasta_origem = f"mesas_ativas/mesa_{id_mesa}"
    pasta_destino = "DENTs/AIs"
    
    # Lista para armazenar os nomes dos arquivos que estão sendo movidos
    arquivos_movidos = []
    
    # Verificando se a pasta de origem existe, se não, criando-a
    if not os.path.exists(pasta_origem):
        os.makedirs(pasta_origem)
    
    # Verificando se a pasta de destino existe, se não, criando-a
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    # Apagando todos os arquivos na pasta de destino
    for arquivo in os.listdir(pasta_destino):
        arquivo_path = os.path.join(pasta_destino, arquivo)
        try:
            if os.path.isfile(arquivo_path):
                os.unlink(arquivo_path)
        except Exception as e:
            print(f"Erro ao apagar {arquivo_path}: {e}")
    
    # Movendo os arquivos da pasta de origem para a pasta de destino
    for indice, arquivo in enumerate(os.listdir(pasta_origem), start=1):
        arquivo_path_origem = os.path.join(pasta_origem, arquivo)
        arquivos_movidos.append(arquivo)  # Adicionando o nome do arquivo à lista
        if arquivo.endswith(".m"):
            novo_nome = f"AI{indice}{os.path.splitext(arquivo)[1]}"
            arquivo_path_destino = os.path.join(pasta_destino, novo_nome)
        else:
            arquivo_path_destino = os.path.join(pasta_destino, arquivo)
        try:
            shutil.move(arquivo_path_origem, arquivo_path_destino)
        except Exception as e:
            print(f"Erro ao mover {arquivo_path_origem} para {arquivo_path_destino}: {e}")
    
    print("Arquivos movidos com sucesso!")
    print("=====================================================================")
    
    return arquivos_movidos

def verificar_codigos():
    return views.verificar_codigos()