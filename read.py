import os
import django
import shutil
import zipfile
import boto3
from botocore.exceptions import ClientError

# 1. Configuração do ambiente Django
# Garante que o script consegue aceder aos modelos do projeto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise
from dents.engine import simular_partida
from dents.infrastructure import criar_pasta_logs

def main():
    print("\n" + "="*60)
    print("🤖 ORQUESTRADOR DEnTS ATIVO")
    print("="*60)

    # --- PASSO 1: VERIFICAR SE EXISTEM MESAS ATIVAS (Status 'Aguardando') ---
    print("\n[1/3] Verificando mesas ativas...")
    lista_id_mesa = analise.criar_pastas_mesas_ativas()

    # --- PASSO 2: SE NÃO HOUVER MESAS, REALIZA NOVO SORTEIO ---
    if not lista_id_mesa:
        print("   🔍 Nenhuma mesa ativa encontrada. Verificando códigos pendentes...")
        
        # Verifica se há jogadores que precisam de mesa (sem mesa ativa ou mesa finalizada)
        if analise.verificar_codigos():
            num_jogadores = analise.numeroJogadores()
            
            if num_jogadores >= 2:
                print(f"   🎲 Sorteando nova rodada para {num_jogadores} jogadores...")
                
                # Obtém IDs, sorteia as mesas e vincula no banco de dados
                lista_ids = analise.get_codigo_ids()
                mesas_sorteadas = analise.sortear_mesas(num_jogadores, lista_ids)
                analise.criar_mesa_e_vincular_codigos(mesas_sorteadas)
                
                print("   ✅ Sorteio concluído e novas mesas criadas.")
                
                # Atualiza a lista para processar as mesas que acabaram de ser criadas
                lista_id_mesa = analise.criar_pastas_mesas_ativas()
            else:
                print(f"   ⚠️ Jogadores insuficientes ({num_jogadores}) para novo sorteio.")
        else:
            print("   💤 Nenhum código disponível para sorteio no momento.")

    # Encerra se após a tentativa de sorteio ainda não houver mesas
    if not lista_id_mesa:
        print("\n" + "="*60)
        print("🏁 FIM DO CICLO: NADA PARA PROCESSAR")
        print("="*60)
        return

    # --- PASSO 3: PROCESSAMENTO DAS PARTIDAS ---
    print(f"\n[2/3] Iniciando Simulações ({len(lista_id_mesa)} mesas)...")
    lista_arquivos_mesas = analise.consultar_arquivo_e_id_mesas()

    for id_mesa in lista_id_mesa:
        print(f"\n>>> EXECUTANDO MESA {id_mesa} <<<")
        
        pasta_mesa = f"./mesas_ativas/mesa_{id_mesa}"
        os.makedirs(pasta_mesa, exist_ok=True)
        
        # Filtra e baixa os arquivos da mesa
        caminhos_s3 = [item[0] for item in lista_arquivos_mesas if item[1] == id_mesa]
        caminhos_locais = []

        for path_s3 in caminhos_s3:
            # A função download_unico_e_extrair deve retornar o caminho local (os.path)
            local = analise.download_unico_e_extrair(path_s3, pasta_mesa)
            if local and os.path.exists(local):
                caminhos_locais.append(local)
                print(f"   🔎 Código verificado: {os.path.basename(local)}")

        # Verificação crucial para evitar o erro 'high <= 0' do NumPy
        if len(caminhos_locais) < 2:
            print(f"   ❌ Erro: Mesa {id_mesa} sem jogadores válidos suficientes. Pulando.")
            continue

        try:
            # Configuração para o motor de jogo
            config = {
                "id_mesa": id_mesa,
                "jogadores": caminhos_locais,
                "numJogadores": len(caminhos_locais), # Define o limite para sorteios aleatórios
                "numTorneios": 10,
                "pasta_logs": criar_pasta_logs()
            }

            print(f"   🎲 Simulando partida com {config['numJogadores']} jogadores...")
            resultado = simular_partida(config)

            # Atualiza o status para 'Finalizado' e liberta os códigos para o próximo sorteio
            analise.finalizar_mesa(id_mesa, resultado)
            print(f"   ✅ Mesa {id_mesa} processada com sucesso.")

        except Exception as e:
            print(f"   ❌ ERRO CRÍTICO na Mesa {id_mesa}: {e}")

    print("\n" + "="*60)
    print("🏁 PROCESSAMENTO CONCLUÍDO")
    print("="*60)

if __name__ == "__main__":
    main()