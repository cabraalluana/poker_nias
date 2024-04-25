import math
import random

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

    print("=====================================================================")
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

    print("=====================================================================")
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