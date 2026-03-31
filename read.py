import os
import django
import shutil
import time
import sys
import boto3
from django.conf import settings

# 1. Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise
from dents.engine import simular_partida
from dents.infrastructure import criar_pasta_logs
from apps.mesas.models import Torneio, ResultadoTorneio, HistoricoPartida

def enviar_para_s3(caminho_local_arquivo, pasta_destino_s3):
    """Faz o upload para o S3 e retorna o caminho relativo."""
    s3 = boto3.client('s3', 
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    nome_arquivo = os.path.basename(caminho_local_arquivo)
    caminho_s3 = f"{pasta_destino_s3}/{nome_arquivo}"
    try:
        s3.upload_file(caminho_local_arquivo, settings.AWS_STORAGE_BUCKET_NAME, caminho_s3)
        return caminho_s3 
    except Exception as e:
        print(f"   ⚠️ Falha no upload S3 ({nome_arquivo}): {e}")
        return caminho_local_arquivo

class Logger(object):
    def __init__(self, filename="log_execucao.txt"):
        self.terminal = sys.stdout
        self.filename = filename
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

def main():
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo_log = f"relatorio_torneio_{timestamp}.txt"
    original_stdout = sys.stdout # Guarda o terminal original
    sys.stdout = Logger(nome_arquivo_log)

    inicio_torneio = time.time() 
    qtd_inicial = analise.numeroJogadores()
    torneio_db = Torneio.objects.create(quantidade_jogadores=qtd_inicial)
    
    primeira_rodada = True
    jogadores_para_proxima_fase = []
    fase_atual = 1

    print("\n" + "="*60)
    print(f"🤖 ORQUESTRADOR DEnTS - TORNEIO ID: {torneio_db.id}")
    print("="*60)

    try:
        while True:
            print(f"\n📢 INICIANDO FASE {fase_atual}...")
            
            if primeira_rodada:
                ids_disponiveis = analise.get_codigo_ids()
                primeira_rodada = False
            else:
                ids_disponiveis = jogadores_para_proxima_fase
            
            if len(ids_disponiveis) < 2: break

            mesas_sorteadas = analise.sortear_mesas(len(ids_disponiveis), ids_disponiveis)
            analise.criar_mesa_e_vincular_codigos(mesas_sorteadas)
            mesas_ativas = analise.criar_pastas_mesas_ativas()
            
            logs_fase, ids_fase, mesas_com_sucesso = [], [], []
            lista_arquivos_mesas = analise.consultar_arquivo_e_id_mesas()

            for id_mesa in mesas_ativas:
                print(f"\n>>> EXECUTANDO MESA {id_mesa} <<<")
                pasta_mesa_local = f"./mesas_ativas/mesa_{id_mesa}"
                os.makedirs(pasta_mesa_local, exist_ok=True)
                
                dados_mesa = [item for item in lista_arquivos_mesas if item[2] == id_mesa]
                caminhos_locais, ids_validos = [], []

                for id_cod, path_s3, _ in dados_mesa:
                    local = analise.download_unico_e_extrair(path_s3, pasta_mesa_local)
                    if local and os.path.exists(local):
                        caminhos_locais.append(local)
                        ids_validos.append(id_cod)

                if len(caminhos_locais) < 2: continue

                try:
                    inicio_mesa = time.time()
                    pasta_log_local = criar_pasta_logs()
                    config = {"id_mesa": id_mesa, "jogadores": caminhos_locais, "numJogadores": len(caminhos_locais), "numTorneios": 10, "pasta_logs": pasta_log_local}
                    simular_partida(config)
                    
                    fim_mesa = time.time()
                    tempo_ms = int((fim_mesa - inicio_mesa) * 1000)

                    arquivo_log_mesa = os.path.join(pasta_log_local, 'log_acoes.txt')
                    caminho_relativo_s3 = enviar_para_s3(arquivo_log_mesa, f"historico_torneios/torneio_{torneio_db.id}/fase_{fase_atual}")

                    HistoricoPartida.objects.create(
                        torneio=torneio_db, mesa_id_original=id_mesa,
                        log_arquivo=caminho_relativo_s3, tempo_processamento_ms=tempo_ms, fase=fase_atual
                    )
                    
                    logs_fase.append(pasta_log_local)
                    ids_fase.append(ids_validos)
                    mesas_com_sucesso.append(id_mesa)
                    analise.finalizar_mesa(id_mesa, None)
                    print(f"   ✅ Mesa {id_mesa} finalizada em {tempo_ms}ms.")
                    
                except Exception as e:
                    print(f"   ❌ Erro na mesa {id_mesa}: {e}")

            if not mesas_com_sucesso: break
            if len(mesas_ativas) > 1:
                jogadores_para_proxima_fase = analise.obter_sobreviventes_da_fase(mesas_com_sucesso, logs_fase, ids_fase)
                fase_atual += 1
            else:
                caminho_log_final = os.path.join(logs_fase[0], 'log_acoes.txt')
                ranking_final = analise.obter_ranking_mesa(caminho_log_final, ids_fase[0])
                for pos, player in enumerate(ranking_final, start=1):
                    ResultadoTorneio.objects.create(torneio=torneio_db, codigo_id=player['id_codigo'], posicao=pos, fichas_finais=player['fichas'])
                break 

    finally:
        # --- FINALIZAÇÃO E LIMPEZA ---
        duracao_total = time.time() - inicio_torneio
        torneio_db.tempo_total_ms = int(duracao_total * 1000)
        torneio_db.save()

        print(f"\n⏱️ TEMPO TOTAL: {int(duracao_total // 60)}m {int(duracao_total % 60)}s")
        
        # Fecha o logger e volta o stdout ao normal
        sys.stdout.log.close()
        sys.stdout = original_stdout

        # 1. Sobe o relatório final para o S3
        url_txt_s3 = enviar_para_s3(nome_arquivo_log, "relatorios_execucao")
        print(f"☁️ Relatório enviado para a AWS.")

        # 2. DELETE: Apaga o arquivo .txt local
        if os.path.exists(nome_arquivo_log):
            os.remove(nome_arquivo_log)
            print(f"🗑️ Arquivo local {nome_arquivo_log} removido.")

        # 3. DELETE: Apaga as pastas temporárias de execução
        pastas_para_limpar = ['./mesas_ativas', './logs']
        for pasta in pastas_para_limpar:
            if os.path.exists(pasta):
                shutil.rmtree(pasta)
                print(f"🧹 Pasta temporária {pasta} limpa.")

        print("🏁 PROCESSO CONCLUÍDO E LIMPO!\n")

if __name__ == "__main__":
    main()