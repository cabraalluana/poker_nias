import os
import django
import shutil
import zipfile
import boto3
from botocore.exceptions import ClientError

# 1. Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise
from dents.engine import simular_partida
from dents.infrastructure import criar_pasta_logs

def main():
    print("\n🚀 ORQUESTRADOR DEnTS ATIVO")
    
    # Busca as mesas prontas para jogar
    lista_id_mesa = analise.criar_pastas_mesas_ativas()
    if not lista_id_mesa:
        print("   💤 Nenhuma mesa pronta.")
        return

    lista_arquivos_mesas = analise.consultar_arquivo_e_id_mesas()

    for id_mesa in lista_id_mesa:
        print(f"\n>>> PROCESSANDO MESA {id_mesa} <<<")
        
        # 1. Cria pasta temporária para esta mesa
        pasta_mesa = f"./mesas_ativas/mesa_{id_mesa}"
        os.makedirs(pasta_mesa, exist_ok=True)
        
        # 2. Busca e baixa os arquivos dos bots
        caminhos_s3 = [item[0] for item in lista_arquivos_mesas if item[1] == id_mesa]
        caminhos_locais = []

        for path_s3 in caminhos_s3:
            local = analise.download_unico_e_extrair(path_s3, pasta_mesa)
            if local and os.path.exists(local): # Verifica se o download realmente salvou algo
                caminhos_locais.append(local)

        # --- CORREÇÃO DO ERRO 'high <= 0' ---
        # Se a lista estiver vazia ou com apenas 1 jogador, o motor trava.
        if len(caminhos_locais) < 2:
            print(f"   ⚠️ Mesa {id_mesa} ignorada: Apenas {len(caminhos_locais)} jogadores válidos encontrados.")
            continue

        try:
            # 3. Executa o motor com a configuração COMPLETA
            config = {
                "id_mesa": id_mesa,
                "jogadores": caminhos_locais,
                "numJogadores": len(caminhos_locais), # <-- ADICIONADO PARA EVITAR O ERRO DO NUMPY
                "numTorneios": 10,
                "pasta_logs": criar_pasta_logs()
            }
            
            print(f"   🎲 Simulando partida com {config['numJogadores']} jogadores...")
            resultado = simular_partida(config)

            # 4. Finaliza no Banco
            analise.finalizar_mesa(id_mesa, resultado)
            print(f"   ✅ Mesa {id_mesa} FINALIZADA.")

        except Exception as e:
            print(f"   ❌ ERRO CRÍTICO na Mesa {id_mesa}: {e}")

if __name__ == "__main__":
    main()