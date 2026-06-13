import os
import django
import shutil
import time
import sys
import boto3
import multiprocessing
from django.conf import settings

if __name__ == '__main__':
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError: pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise
from dents.engine import simular_partida
from dents.infrastructure import criar_pasta_logs
from apps.mesas.models import Torneio, ResultadoTorneio, HistoricoPartida

def salvar_log_localmente(caminho_local_arquivo, pasta_destino_local="media/logs"):
    """
    Substitui o antigo envio para o AWS S3.
    Garante a persistência do arquivo de log na pasta de mídia local do servidor.
    """
    nome_arquivo = os.path.basename(caminho_local_arquivo)
    diretorio_destino = os.path.join(settings.BASE_DIR, pasta_destino_local)
    
    # Garante que a pasta de destino exista
    if not os.path.exists(diretorio_destino):
        os.makedirs(diretorio_destino, exist_ok=True)
        
    caminho_final = os.path.join(diretorio_destino, nome_arquivo)
    
    try:
        shutil.copy2(caminho_local_arquivo, caminho_final)
        return f"{pasta_destino_local}/{nome_arquivo}"
    except Exception as e:
        print(f"⚠️ Falha ao mover log localmente: {e}")
        return caminho_local_arquivo

class Logger(object):
    def __init__(self, filename="log_execucao.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message); self.log.write(message)
    def flush(self): pass

def main():
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo_log = f"relatorio_torneio_{timestamp}.txt"
    sys.stdout = Logger(nome_arquivo_log)
    inicio_torneio = time.time() 
    torneio_db = Torneio.objects.create(quantidade_jogadores=analise.numeroJogadores())
    primeira_rodada, jogadores_para_proxima_fase, fase_atual = True, [], 1

    print(f"\n🤖 ORQUESTRADOR DEnTS - ID: {torneio_db.id} (MODO BLINDADO)")
    try:
        while True:
            print(f"\n📢 INICIANDO FASE {fase_atual}...")
            ids_disponiveis = analise.get_codigo_ids() if primeira_rodada else jogadores_para_proxima_fase
            primeira_rodada = False
            if len(ids_disponiveis) < 2: break

            mesas_sorteadas = analise.sortear_mesas(len(ids_disponiveis), ids_disponiveis)
            analise.criar_mesa_e_vincular_codigos(mesas_sorteadas, torneio_db)
            mesas_ativas = analise.criar_pastas_mesas_ativas()
            logs_fase, ids_fase, mesas_com_sucesso = [], [], []
            lista_arquivos_mesas = analise.consultar_arquivo_e_id_mesas(torneio_db.id)

            for id_mesa in mesas_ativas:
                id_mesa_int = int(id_mesa)
                print(f"\n>>> PROCESSANDO MESA {id_mesa_int}")
                dados_mesa = [item for item in lista_arquivos_mesas if len(item) > 2 and int(item[2]) == id_mesa_int]
                
                pasta_mesa_local = f"./mesas_ativas/mesa_{id_mesa_int}"
                os.makedirs(pasta_mesa_local, exist_ok=True)
                caminhos_locais, ids_validos = [], []

                for id_cod, path_s3, _ in dados_mesa:
                    local = analise.download_unico_e_extrair(path_s3, pasta_mesa_local)
                    if local: caminhos_locais.append(local); ids_validos.append(id_cod)

                if len(caminhos_locais) < 2:
                    print(f"   ⚠️ Mesa {id_mesa_int} cancelada: bots insuficientes.")
                    analise.finalizar_mesa(id_mesa_int, None); continue

                pasta_log_local = criar_pasta_logs()
                config = {"id_mesa": id_mesa_int, "jogadores": caminhos_locais, "numTorneios": 10, "pasta_logs": pasta_log_local}
                proc = multiprocessing.Process(target=simular_partida, args=(config,))
                proc.start(); proc.join(timeout=30) 

                if proc.is_alive():
                    proc.terminate(); proc.join()
                    HistoricoPartida.objects.create(torneio=torneio_db, mesa_id_original=id_mesa_int, status_execucao='timeout', fase=fase_atual)
                elif proc.exitcode != 0:
                    HistoricoPartida.objects.create(torneio=torneio_db, mesa_id_original=id_mesa_int, status_execucao='erro_bot', fase=fase_atual)
                else:
                    log_file = os.path.join(pasta_log_local, 'log_acoes.txt')
                    if os.path.exists(log_file):
                        s3_p = salvar_log_localmente(log_file, f"media/logs/torneio_{torneio_db.id}/fase_{fase_atual}")
                        HistoricoPartida.objects.create(torneio=torneio_db, mesa_id_original=id_mesa_int, log_arquivo=s3_p, status_execucao='sucesso', fase=fase_atual)
                        logs_fase.append(pasta_log_local); ids_fase.append(ids_validos); mesas_com_sucesso.append(id_mesa_int)
                        analise.finalizar_mesa(id_mesa_int, None)

            if not mesas_com_sucesso: break
            jogadores_para_proxima_fase = analise.obter_sobreviventes_da_fase(mesas_com_sucesso, logs_fase, ids_fase)
            if len(jogadores_para_proxima_fase) < 2: break 

            # --- NOVO: CORTE DE SEGURANÇA (BOTÃO DE PÂNICO) ---
            if fase_atual >= 10:
                print("\n🚨 LIMITE DE FASES ATINGIDO! Os bots empataram infinitamente.")
                # Força o encerramento da competição
                ranking_f = analise.obter_ranking_mesa(os.path.join(logs_fase[0], 'log_acoes.txt'), ids_fase[0])
                for pos, p in enumerate(ranking_f, 1):
                    ResultadoTorneio.objects.create(torneio=torneio_db, codigo_id=p['id_codigo'], posicao=pos, fichas_finais=p['fichas'])
                break
            # --------------------------------------------------
            
            if len(mesas_ativas) > 1: fase_atual += 1
            else:
                ranking_f = analise.obter_ranking_mesa(os.path.join(logs_fase[0], 'log_acoes.txt'), ids_fase[0])
                for pos, p in enumerate(ranking_f, 1):
                    ResultadoTorneio.objects.create(torneio=torneio_db, codigo_id=p['id_codigo'], posicao=pos, fichas_finais=p['fichas'])
                break 
    finally:
        torneio_db.tempo_total_ms = int((time.time() - inicio_torneio) * 1000); torneio_db.save()
        sys.stdout.log.close(); sys.stdout = sys.__stdout__
        salvar_log_localmente(nome_arquivo_log, "media/relatorios_execucao")
        if os.path.exists(nome_arquivo_log): os.remove(nome_arquivo_log)
        for p in ['./mesas_ativas', './logs']: shutil.rmtree(p, ignore_errors=True)
        print("\n🏁 PROCESSO FINALIZADO.")

if __name__ == "__main__":
    multiprocessing.freeze_support(); main()    