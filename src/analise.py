import math
import random
import os
import shutil
import zipfile
from apps.mesas import views

def numeroJogadores(): return views.numeroJogadores()
def get_codigo_ids(): return views.get_codigo_ids()

def encontrar_n(num):
    if num <= 10: return 1
    for n in range(2, num):
        if (num/n) > 3 and (num/n) <= 10: return n
    return 1

def numeroJogadoresMesa(num):
    n = encontrar_n(num)
    res, dist = num, []
    for i in range(n or 1):
        qtd = math.ceil(res / (n - i)) if n else num
        dist.append(qtd); res -= qtd
    return dist

def sortear_mesas(num, ids):
    dist = numeroJogadoresMesa(num)
    random.shuffle(ids)
    mesas, idx = [], 0
    for qtd in dist:
        mesas.append(ids[idx : idx + qtd]); idx += qtd
    return mesas

def criar_mesa_e_vincular_codigos(mesas_sorteadas, torneio_obj):
    from apps.mesas.models import Mesa, Codigo, Codigo_Mesa 
    for grupo in mesas_sorteadas:
        nova_mesa = Mesa.objects.create(status=True, torneio=torneio_obj)
        for codigo_id in grupo:
            codigo_obj = Codigo.objects.get(id=codigo_id)
            Codigo_Mesa.objects.create(codigo=codigo_obj, mesa=nova_mesa)
    print(f"   ✅ {len(mesas_sorteadas)} mesas vinculadas ao Torneio {torneio_obj.id}.")

def criar_pastas_mesas_ativas(): return views.criar_pastas_mesas_ativas()

def consultar_arquivo_e_id_mesas(torneio_id):
    from apps.mesas.models import Codigo_Mesa
    vinculos = Codigo_Mesa.objects.filter(mesa__torneio_id=torneio_id, mesa__status=True)
    resultado = []
    for v in vinculos:
        resultado.append((v.codigo.id, str(v.codigo.arquivo), v.mesa_id))
    return resultado

def download_unico_e_extrair(arquivo_nome, pasta_destino):
    import boto3
    from django.conf import settings
    s3 = boto3.client('s3', 
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    bucket_name = 'fotografias-poker'
    s3_folder = 'static/arquivos/' 
    file_name = os.path.basename(arquivo_nome) 
    s3_key = f"{s3_folder}{file_name}"
    local_path = os.path.join(pasta_destino, file_name)
    if not os.path.exists(pasta_destino): os.makedirs(pasta_destino)
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(local_path, 'r') as zip_ref:
                zip_ref.extractall(pasta_destino)
            if os.path.exists(local_path): os.remove(local_path)
            return os.path.join(pasta_destino, 'bot.py') 
        return local_path 
    except Exception as e:
        print(f"   ❌ Erro S3 no arquivo {file_name}: {e}")
        return None

def finalizar_mesa(id_m, r): return views.alterar_status_mesa(id_m)

def obter_ranking_mesa(caminho, ids):
    """Lê o ranking baseado no formato de espaços do state.py."""
    if not os.path.exists(caminho):
        return [{'id_codigo': i, 'fichas': 0.0} for i in ids]
    try:
        with open(caminho, 'r') as f:
            linhas = f.readlines()
        if not linhas: raise ValueError
        
        # Pega a última linha e divide por espaços (formato do state.py)
        parts = linhas[-1].strip().split()
        
        # No seu state.py, as fichas começam após os 5 primeiros campos (T, M, A, B, P)
        # Então pegamos os últimos N elementos, onde N é o número de jogadores
        num_jogadores = len(ids)
        stacks = parts[-num_jogadores:]
        
        ranking = []
        for i, id_c in enumerate(ids):
            fichas = float(stacks[i]) if i < len(stacks) else 0.0
            ranking.append({'id_codigo': id_c, 'fichas': fichas})
            
        return sorted(ranking, key=lambda x: x['fichas'], reverse=True)
    except Exception as e:
        print(f"   ⚠️ Falha ao ler ranking: {e}")
        return [{'id_codigo': i, 'fichas': 0.0} for i in ids]

def obter_sobreviventes_da_fase(mesas_ok, logs, ids_lista):
    promovidos, eliminados_vivos = [], []
    for i, id_m in enumerate(mesas_ok):
        path = os.path.join(logs[i], 'log_acoes.txt')
        ranking = obter_ranking_mesa(path, ids_lista[i])
        # Promove metade da mesa (5 de 10)
        vagas = max(1, len(ranking) // 2)
        for j, p in enumerate(ranking):
            if j < vagas and p['fichas'] > 0: promovidos.append(p['id_codigo'])
            elif p['fichas'] > 0: eliminados_vivos.append(p)
    
    # Repescagem: Garante que tenhamos pelo menos 2 para a próxima fase
    if len(promovidos) < 2 and eliminados_vivos:
        eliminados_vivos.sort(key=lambda x: x['fichas'], reverse=True)
        while len(promovidos) < 2 and eliminados_vivos:
            promovidos.append(eliminados_vivos.pop(0)['id_codigo'])
    return promovidos