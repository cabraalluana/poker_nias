import os
import glob
import re
import matplotlib.pyplot as plt

def ler_e_processar_log(caminho_log):
    """
    Lê a matriz numérica do log de ações e extrai o saldo final
    de cada bot ao final de cada mão, separando por partida.
    """
    saldos_por_mao = {}
    with open(caminho_log, 'r', encoding='utf-8') as f:
        for linha in f:
            if not linha.strip():
                continue
            valores = linha.strip().split()
            if len(valores) > 5:
                try:
                    # A matriz tem a partida na coluna 0 e a mão na coluna 1
                    partida = int(float(valores[0]))
                    mao = int(float(valores[1]))
                    saldos_bots = [float(v) for v in valores[5:]]
                    
                    # Usa uma tupla (partida, mão) para não haver sobreposição de dados
                    chave = (partida, mao)
                    saldos_por_mao[chave] = saldos_bots
                except (ValueError, IndexError):
                    continue
    return saldos_por_mao

def gerar_grafico_mesa(saldos_por_mao, nome_torneio, nome_fase, nome_mesa, pasta_saida_base):
    if not saldos_por_mao:
        print(f"⚠️ Sem dados válidos para desenhar na {nome_mesa}.")
        return
        
    # Ordena as chaves cronologicamente (Partida 1 -> Mão 1 até Partida 10 -> Última Mão)
    chaves_ordenadas = sorted(saldos_por_mao.keys())
    qtd_bots = len(saldos_por_mao[chaves_ordenadas[0]])
    
    historico_bots = {f"Bot {i+1}": [] for i in range(qtd_bots)}
    for chave in chaves_ordenadas:
        saldos = saldos_por_mao[chave]
        for i in range(qtd_bots):
            historico_bots[f"Bot {i+1}"].append(saldos[i])
            
    # Cria um eixo X contínuo (mão 1 até à mão total jogada nas 10 partidas)
    eixo_x = list(range(1, len(chaves_ordenadas) + 1))
            
    plt.figure(figsize=(14, 7))
    for nome_bot, fichas in historico_bots.items():
        # Removido o 'marker' para evitar demasiada poluição visual com tantos pontos
        plt.plot(eixo_x, fichas, label=nome_bot, linewidth=1.5, alpha=0.85)
        
    plt.title(f'{nome_torneio.upper()} - {nome_fase.upper()} - {nome_mesa.upper()}\nEvolução de Fichas (10 Partidas Contínuas)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Total de Mãos Jogadas (Acumulado)', fontsize=12)
    plt.ylabel('Saldo de Fichas', fontsize=12)
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.5) # Linha de falência
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), title="Competidores")
    plt.tight_layout()
    
    pasta_final_imagem = os.path.join(pasta_saida_base, nome_torneio, nome_fase)
    os.makedirs(pasta_final_imagem, exist_ok=True)
    
    caminho_imagem = os.path.join(pasta_final_imagem, f"grafico_{nome_mesa}.png")
    plt.savefig(caminho_imagem, dpi=300, bbox_inches='tight')
    plt.close() # Libera a memória para não sobrecarregar o Docker
    print(f"✅ Gráfico salvo com sucesso: {caminho_imagem}")

def main():
    pasta_logs_base = './media/logs'
    pasta_resultados_base = './media/resultados_tcc'
    
    if not os.path.exists(pasta_logs_base):
        print(f"❌ Pasta base de logs não encontrada: {pasta_logs_base}")
        return
        
    pastas_torneios = glob.glob(os.path.join(pasta_logs_base, 'torneio_*'))
    if not pastas_torneios:
        print("❌ Nenhum diretório de torneio encontrado em ./media/logs/")
        return
        
    def extrair_id_torneio(caminho):
        match = re.search(r'torneio_(\d+)', caminho)
        return int(match.group(1)) if match else 0

    diretorio_ultimo_torneio = max(pastas_torneios, key=extrair_id_torneio)
    nome_ultimo_torneio = os.path.basename(diretorio_ultimo_torneio)
    
    print(f"🎯 Último Torneio Detectado: {nome_ultimo_torneio}")
    
    padrao_busca_mesas = os.path.join(diretorio_ultimo_torneio, 'fase_*', 'log_acoes_mesa_*.txt')
    arquivos_mesas = glob.glob(padrao_busca_mesas)
    
    if not arquivos_mesas:
        print(f"⚠️ Nenhum log de mesa com o padrão 'log_acoes_mesa_*.txt' foi achado em {nome_ultimo_torneio}")
        return
        
    print(f"📂 Encontrados {len(arquivos_mesas)} ficheiros de mesas para processar.\n")
    
    for caminho_arquivo in arquivos_mesas:
        match_fase = re.search(r'(fase_\d+)', caminho_arquivo)
        match_mesa = re.search(r'(mesa_\d+)', os.path.basename(caminho_arquivo))
        
        nome_fase = match_fase.group(1) if match_fase else "fase_indefinida"
        nome_mesa = match_mesa.group(1) if match_mesa else "mesa_indefinida"
        
        print(f"🔄 Processando {nome_fase} ➔ {nome_mesa}...")
        
        dados_log = ler_e_processar_log(caminho_arquivo)
        gerar_grafico_mesa(dados_log, nome_ultimo_torneio, nome_fase, nome_mesa, pasta_resultados_base)
        
    print(f"\n🏁 Análise finalizada! Todos os gráficos disponíveis em: {pasta_resultados_base}/{nome_ultimo_torneio}/")

if __name__ == "__main__":
    main()