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

def download_unico_e_extrair(arquivo_nome, pasta_destino):
    """
    BAIXA DO S3 E RETORNA O CAMINHO LOCAL.
    Esta função resolve o erro de '0 jogadores válidos'.
    """
    import boto3
    import os
    import zipfile

    s3 = boto3.client('s3')
    bucket_name = 'fotografias-poker'
    s3_folder = 'static/arquivos/' 
    
    file_name = os.path.basename(arquivo_nome) 
    s3_key = f"{s3_folder}{file_name}"
    local_path = os.path.join(pasta_destino, file_name)

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    try:
        print(f"   📥 Baixando '{file_name}'...")
        s3.download_file(bucket_name, s3_key, local_path)
        
        # Se for ZIP, extrai e retorna o caminho do bot lá dentro
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(local_path, 'r') as zip_ref:
                zip_ref.extractall(pasta_destino)
            os.remove(local_path)
            # Retorna o caminho do arquivo principal (ajuste se for outro nome)
            return os.path.join(pasta_destino, 'bot.py') 

        # RETORNO CRUCIAL: Retorna o caminho do .py para o read.py
        print(f"   ✅ Download concluído: {local_path}")
        return local_path 

    except Exception as e:
        print(f"   ❌ Erro no download/extração: {e}")
        return None

def finalizar_mesa(id_mesa, resultado):
    """
    Altera o status da mesa para desativado (False) após a simulação.
    """
    # Import local para evitar problemas de carregamento do Django
    from apps.mesas.models import Mesa 
    
    try:
        mesa = Mesa.objects.get(id=id_mesa)
        # De acordo com a sua lógica: True = Ativa, False = Desativada
        mesa.status = False 
        mesa.save()
        
        print(f"   🏁 SUCESSO: Mesa {id_mesa} desativada no Banco de Dados.")
        
        # Opcional: Aqui você também pode salvar o 'resultado' em um campo de Log na Mesa
        # mesa.log_resultado = str(resultado)
        # mesa.save()

    except Mesa.DoesNotExist:
        print(f"   ⚠️ ERRO: Mesa {id_mesa} não encontrada para finalizar.")
    except Exception as e:
        print(f"   ⚠️ ERRO ao atualizar status da mesa {id_mesa}: {e}")

def obter_vencedor_log(caminho_log, lista_jogadores):
    """
    Lê a última linha do log e retorna o nome do vencedor.
    """
    try:
        with open(caminho_log, 'r') as f:
            linhas = f.readlines()
            if not linhas:
                return "Log vazio"
            
            # Pega a última linha e transforma em lista de números
            ultima_linha = linhas[-1].split()
            # Os stacks começam a partir do índice 5 (após torneio, fase, acao, aposta e pote)
            stacks = [float(s) for s in ultima_linha[5:]]
            
            # Encontra o índice do maior stack
            indice_vencedor = stacks.index(max(stacks))
            
            # Mapeia o índice para o nome do arquivo/usuário
            path_vencedor = lista_jogadores[indice_vencedor]
            nome_vencedor = os.path.basename(path_vencedor).replace('bot_', '').replace('.py', '')
            
            return nome_vencedor.capitalize()
    except Exception as e:
        return f"Erro ao ler vencedor: {e}"

def promover_jogadores(id_mesas_finalizadas, pasta_dos_logs):
    """Pasta_dos_logs deve ser a mesma 'Log-YYYY...' gerada pelo read.py"""
    classificados = []
    for id_mesa in id_mesas_finalizadas:
        # Busca o log dentro da pasta timestamped do dia
        caminho_log = os.path.join(pasta_dos_logs, 'log_acoes.txt') 
        
        # Precisamos dos IDs que estavam naquela mesa específica
        from apps.mesas.models import Mesa
        ids_mesa = list(Mesa.objects.get(id=id_mesa).codigos_participantes.values_list('id', flat=True))
        
        ranking = obter_ranking_mesa(caminho_log, ids_mesa)
        
        # Promove os 50% melhores
        corte = len(ranking) // 2
        for i in range(corte):
            classificados.append(ranking[i]['id_codigo'])
            
    return classificados

def consultar_arquivo_e_id_mesas():
    """Retorna lista de (id_codigo, caminho_s3, id_mesa) usando a tabela ponte."""
    from apps.mesas.models import Mesa, Codigo_Mesa
    mesas_ativas = Mesa.objects.filter(status=True)
    resultado = []
    
    for mesa in mesas_ativas:
        # Filtra na tabela ponte 'Codigo_Mesa'
        vinculos = Codigo_Mesa.objects.filter(mesa=mesa)
        for v in vinculos:
            # Retorna ID, Caminho do arquivo e ID da mesa
            resultado.append((v.codigo.id, v.codigo.arquivo.name, mesa.id))
    return resultado

def criar_mesa_e_vincular_codigos(mesas_sorteadas):
    """
    Cria os objetos Mesa e estabelece o vínculo na tabela ponte Codigo_Mesa.
    """
    from apps.mesas.models import Mesa, Codigo, Codigo_Mesa 

    for grupo in mesas_sorteadas:
        # 1. Cria a Mesa - Usando apenas o campo 'status', que é o único disponível
        nova_mesa = Mesa.objects.create(
            status=True
        )
        
        # 2. Vincula cada ID de código a esta nova mesa na tabela ponte
        for codigo_id in grupo:
            codigo_obj = Codigo.objects.get(id=codigo_id) #
            
            # Cria o vínculo na tabela intermediária Codigo_Mesa
            Codigo_Mesa.objects.create(
                codigo=codigo_obj,
                mesa=nova_mesa
            )
            
    print("   ✅ Mesas e códigos vinculados com sucesso na tabela ponte.")

def obter_ranking_mesa(caminho_log, lista_ids_jogadores):
    """Lê o log e retorna lista ordenada. Inclui o ID para o funil."""
    from apps.mesas.models import Codigo
    with open(caminho_log, 'r') as f:
        linhas = f.readlines()
    if not linhas: return []
    
    ultima_linha = linhas[-1].split()
    # Stacks finais começam no índice 5 no log_acoes.txt
    stacks_finais = [float(s) for s in ultima_linha[5:]]
    
    ranking = []
    for i, stack in enumerate(stacks_finais):
        id_atual = lista_ids_jogadores[i]
        # Busca o nome do aluno usando o relacionamento 'usuario'
        nome = Codigo.objects.get(id=id_atual).usuario.first_name 
        ranking.append({
            "id_codigo": id_atual,  # ADICIONADO: Necessário para a promoção de fase
            "nome": nome.capitalize(), 
            "fichas": stack
        })
    
    # Ordena do maior stack para o menor
    return sorted(ranking, key=lambda x: x['fichas'], reverse=True)

def obter_classificados_torneio(id_mesas_finalizadas, logs_paths):
    """
    Lê os logs das mesas terminadas e retorna apenas os IDs dos 
    5 melhores de cada uma para a próxima fase.
    """
    classificados = []
    for i, id_mesa in enumerate(id_mesas_finalizadas):
        # Gera o ranking daquela mesa específica
        ranking = obter_ranking_mesa(logs_paths[i], ids_jogadores_da_mesa)
        
        # Pega os 5 primeiros (Top 50%)
        for j in range(5):
            classificados.append(ranking[j]['id'])
            
    return classificados # Retorna a lista de 10 IDs para a Mesa Final

def promover_vencedores(id_mesa, ranking):
    """
    Promove o Top 50% dos jogadores. Remove o vínculo da mesa atual
    para que fiquem 'livres' para o próximo sorteio (Fase Final).
    """
    from apps.mesas.models import Codigo_Mesa
    # Em uma mesa de 10, promovemos os 5 primeiros
    qtd_vagas = len(ranking) // 2
    
    for i in range(qtd_vagas):
        id_cod = ranking[i]['id']
        # Ao deletar o vínculo aqui, o 'verificar_codigos()' voltará a ver este ID como disponível
        Codigo_Mesa.objects.filter(codigo_id=id_cod, mesa_id=id_mesa).delete()
    
    print(f"   📣 {qtd_vagas} jogadores promovidos para a próxima fase.")

def obter_sobreviventes_da_fase(ids_mesas_rodadas, pastas_logs, lista_ids_por_mesa):
    """
    Recebe as mesas que acabaram de rodar e devolve os 5 melhores de cada.
    """
    promovidos = []
    for i, id_mesa in enumerate(ids_mesas_rodadas):
        caminho_log = os.path.join(pastas_logs[i], 'log_acoes.txt')
        # Pega o ranking daquela mesa específica
        ranking = obter_ranking_mesa(caminho_log, lista_ids_por_mesa[i])
        
        # Pega os 5 primeiros (Top 50%)
        for j in range(min(5, len(ranking))):
            promovidos.append(ranking[j]['id_codigo'])
            
    return promovidos # IDs prontos para a próxima rodada