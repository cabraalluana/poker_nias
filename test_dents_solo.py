import os
from dents.engine import simular_partida

def testar_motor():
    print("\n🚀 INICIANDO TESTE ISOLADO DO MOTOR DEnTS")
    
    # 1. Definir um caminho de log manual e GARANTIR que a pasta existe
    caminho_teste = "./logs/teste_manual"
    if not os.path.exists(caminho_teste):
        os.makedirs(caminho_teste)
        print(f"✅ Pasta de log criada em: {os.path.abspath(caminho_teste)}")

    # 2. Montar a configuração mínima que o joga.py (engine) espera
    config = {
        "numTorneios": 5,           # Menos torneios para ser rápido
        "jogadores": ["bot_teste.py", "bot_teste.py", "bot_teste.py"],
        "pasta_logs": caminho_teste,
        "flagLogs": True,           # ESSENCIAL: Sem isso o state.py não grava nada!
        "estruturaApostas": 4
    }

    try:
        print("🎲 Chamando simular_partida...")
        resultados = simular_partida(config)
        
        print("\n📊 RESULTADOS OBTIDOS:")
        print(resultados)
        
        # 3. Verificar se os arquivos apareceram
        arquivos = os.listdir(caminho_teste)
        if arquivos:
            print(f"\n✨ SUCESSO! Arquivos gerados: {arquivos}")
        else:
            print("\n❌ ERRO: O motor rodou, mas a pasta continua vazia.")
            print("Verifique se o engine.py está chamando 'estado.exporta_acoes()'.")

    except Exception as e:
        print(f"\n💥 FALHA NO MOTOR: {e}")

if __name__ == "__main__":
    testar_motor()