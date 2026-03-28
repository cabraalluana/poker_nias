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

    # 1. Busca mesas ativas ou realiza novo sorteio
    lista_id_mesa = analise.criar_pastas_mesas_ativas()

    if not lista_id_mesa:
        if analise.verificar_codigos():
            num_jogadores = analise.numeroJogadores()
            if num_jogadores >= 2:
                lista_ids = analise.get_codigo_ids()
                mesas_sorteadas = analise.sortear_mesas(num_jogadores, lista_ids)
                analise.criar_mesa_e_vincular_codigos(mesas_sorteadas)
                lista_id_mesa = analise.criar_pastas_mesas_ativas()

    if not lista_id_mesa:
        print("\n🏁 NADA PARA PROCESSAR.")
        return

    # 2. Processamento das Partidas
    lista_arquivos_mesas = analise.consultar_arquivo_e_id_mesas()

    for id_mesa in lista_id_mesa:
        print(f"\n>>> EXECUTANDO MESA {id_mesa} <<<")
        pasta_mesa = f"./mesas_ativas/mesa_{id_mesa}"
        os.makedirs(pasta_mesa, exist_ok=True)
        
        caminhos_s3 = [item[0] for item in lista_arquivos_mesas if item[1] == id_mesa]
        caminhos_locais = []

        for path_s3 in caminhos_s3:
            local = analise.download_unico_e_extrair(path_s3, pasta_mesa)
            if local and os.path.exists(local):
                caminhos_locais.append(local)

        if len(caminhos_locais) < 2:
            print(f"   ❌ Erro: Jogadores insuficientes na Mesa {id_mesa}.")
            continue

        # --- BLOCO NOVO: MAPEAMENTO DE USUÁRIOS ---
        print(f"\n   --- Formação da Mesa {id_mesa} ---")
        for i, path in enumerate(caminhos_locais):
            # Limpa o nome do arquivo para mostrar apenas o nome do aluno
            nome_aluno = os.path.basename(path).replace('bot_', '').replace('.py', '')
            print(f"   👤 Bot {i+1}: {nome_aluno.capitalize()}")
        print("   --------------------------------\n")

        try:
            config = {
                "id_mesa": id_mesa,
                "jogadores": caminhos_locais,
                "numJogadores": len(caminhos_locais),
                "numTorneios": 10,
                "pasta_logs": criar_pasta_logs()
            }

            print(f"   🎲 Simulando partida...")
            resultado = simular_partida(config)
            
            caminho_log_final = os.path.join(config['pasta_logs'], 'log_acoes.txt')
            vencedor = analise.obter_vencedor_log(caminho_log_final, caminhos_locais)
            
            print("\n" + "🏆" + "-"*30)
            print(f"   VENCEDOR DA MESA: {vencedor}")
            print("-"*32 + "\n")
            # ----------------------------------------

            analise.finalizar_mesa(id_mesa, resultado)

        except Exception as e:
            print(f"   ❌ ERRO na Mesa {id_mesa}: {e}")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()