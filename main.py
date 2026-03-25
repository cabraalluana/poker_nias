# main.py (ou web/app/main_dents.py)
import time
import os
from dents.config import obter_configuracao
from dents.analytics import declarar_resultados, salvar_resultados_csv

# Importaremos o engine que traduziremos no próximo passo
# from dents.engine import rodar_simulacao 

def executar_dents():
    print("============================= Iniciando DEnTS (Python) =============================")
    
    # 1. Configura o jogo
    # Substitui: [jogadores, tightness, estruturaApostas, tipoJogo, numTorneios, tempoSimulacao, flagLogs, flagHuman] = configura_jogo;
    config = obter_configuracao()
    
    # 2. Cria pasta de logs
    # Substitui: f = cria_pasta_logs;
    pasta_logs = "./logs/simulacao"
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)
    
    # 3. Inicia Cronômetro
    # Substitui: tic;
    inicio_tempo = time.time()
    
    print(f"Executando {config['numTorneios']} torneios...")
    
    # 4. Executa a Simulação (Core do Sistema)
    # Substitui: [resultados, t] = joga(...);
    # Por enquanto, usaremos um placeholder até traduzirmos o engine.py
    # resultados, tempos_partidas = rodar_simulacao(config) 
    
    # --- SIMULAÇÃO DE DADOS PARA TESTE (APAGAR APÓS TRADUZIR ENGINE.PY) ---
    import numpy as np
    resultados = np.random.randint(1, config['numJogadores'] + 1, size=(config['numTorneios'], config['numJogadores']))
    tempos_partidas = [0.1] * config['numTorneios']
    # ---------------------------------------------------------------------

    # 5. Finaliza Cronômetro
    # Substitui: tempo_total = toc;
    tempo_total = time.time() - inicio_tempo
    
    # 6. Declara e Salva Resultados
    # Substitui: salva_resultados_csv(..., f);
    absoluto, porcentagem, media_pontos = declarar_resultados(resultados, config)
    caminho_csv = salvar_resultados_csv(config['jogadores'], media_pontos, pasta_logs)
    
    print("=======================================================================")
    print(f"✅ Simulação concluída com sucesso!")
    print(f"⏱️ Tempo total: {tempo_total:.4f} segundos")
    print(f"📊 Resultados salvos em: {caminho_csv}")

if __name__ == "__main__":
    executar_dents()