import os
import django
import shutil
import time

# Configurações Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise
from dents.engine import simular_partida
from dents.infrastructure import criar_pasta_logs

def main():
    # --- CRONÔMETRO GLOBAL ---
    inicio_torneio = time.time() 
    
    primeira_rodada = True
    jogadores_para_proxima_fase = []
    fase_atual = 1

    print("\n" + "="*60)
    print("🤖 ORQUESTRADOR DEnTS - MODO FUNIL (MTT)")
    print("="*60)

    while True:
        print(f"\n📢 INICIANDO FASE {fase_atual}...")
        
        # --- PASSO 1: SORTEIO / SELEÇÃO ---
        if primeira_rodada:
            ids_disponiveis = analise.get_codigo_ids()
            primeira_rodada = False
        else:
            ids_disponiveis = jogadores_para_proxima_fase
        
        if len(ids_disponiveis) < 2:
            print("🏁 Fim do processamento: Jogadores insuficientes para nova fase.")
            break

        # Sorteia e vincula no banco
        mesas_sorteadas = analise.sortear_mesas(len(ids_disponiveis), ids_disponiveis)
        analise.criar_mesa_e_vincular_codigos(mesas_sorteadas)
        
        mesas_ativas = analise.criar_pastas_mesas_ativas()
        num_mesas = len(mesas_ativas)
        
        logs_fase, ids_fase = [], []
        lista_arquivos_mesas = analise.consultar_arquivo_e_id_mesas()

        # --- PASSO 2: EXECUÇÃO DAS MESAS ---
        for id_mesa in mesas_ativas:
            print(f"\n>>> EXECUTANDO MESA {id_mesa} <<<")
            pasta_mesa = f"./mesas_ativas/mesa_{id_mesa}"
            os.makedirs(pasta_mesa, exist_ok=True)
            
            # Filtra os dados desta mesa
            dados_mesa = [item for item in lista_arquivos_mesas if item[2] == id_mesa]
            caminhos_locais = []
            ids_validos = []

            for id_cod, path_s3, _ in dados_mesa:
                local = analise.download_unico_e_extrair(path_s3, pasta_mesa)
                if local and os.path.exists(local):
                    caminhos_locais.append(local)
                    ids_validos.append(id_cod)

            if len(caminhos_locais) < 2:
                print(f"   ❌ Erro: Jogadores insuficientes na Mesa {id_mesa}.")
                continue

            try:
                pasta_log = criar_pasta_logs()
                config = {
                    "id_mesa": id_mesa, 
                    "jogadores": caminhos_locais, 
                    "numJogadores": len(caminhos_locais), 
                    "numTorneios": 10, 
                    "pasta_logs": pasta_log
                }
                
                print(f"   🎲 Simulando partida...")
                simular_partida(config)
                
                # Armazena dados para o ranking/promoção
                logs_fase.append(pasta_log)
                ids_fase.append(ids_validos)
                
                analise.finalizar_mesa(id_mesa, None)
                print(f"   ✅ Mesa {id_mesa} finalizada.")
                
            except Exception as e:
                print(f"   ❌ Erro na mesa {id_mesa}: {e}")

        # --- PASSO 3: RANKING DEFINITIVO OU PROMOÇÃO ---
        if not logs_fase:
            print("❌ Nenhuma mesa foi processada com sucesso nesta fase. Abortando.")
            break

        if num_mesas > 1:
            print(f"\n🔄 FASE {fase_atual} CONCLUÍDA. Promovendo vencedores...")
            jogadores_para_proxima_fase = analise.obter_sobreviventes_da_fase(mesas_ativas, logs_fase, ids_fase)
            fase_atual += 1
        else:
            # --- MESA FINAL ---
            print("\n" + "⭐"*20)
            print("🏆 RANKING DEFINITIVO DO TORNEIO 🏆")
            print("⭐"*20)
            
            ranking_final = analise.obter_ranking_mesa(os.path.join(logs_fase[0], 'log_acoes.txt'), ids_fase[0])
            
            for pos, player in enumerate(ranking_final, start=1):
                medalha = "🥇" if pos == 1 else "🥈" if pos == 2 else "🥉" if pos == 3 else f"{pos}º"
                print(f"   {medalha} {player['nome']}: {player['fichas']:.2f} fichas")
            
            print("="*60)
            break 

    # --- TEMPO TOTAL ---
    tempo_total = time.time() - inicio_torneio
    minutos = int(tempo_total // 60)
    segundos = int(tempo_total % 60)
    
    print(f"\n⏱️ TEMPO TOTAL DE PROCESSAMENTO: {minutos}m {segundos}s")
    print("🏁 PROCESSO CONCLUÍDO COM SUCESSO!\n")

if __name__ == "__main__":
    main()