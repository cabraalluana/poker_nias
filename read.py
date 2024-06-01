import os
import django
import schedule

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise
import time as tm
from datetime import time, timedelta, datetime

def apagar_conteudo_pasta(pasta):
    try:
        # Verifica se a pasta existe
        if os.path.exists(pasta):
            # Percorre todos os arquivos e subpastas dentro da pasta
            for arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, arquivo)
                # Remove o arquivo se for um arquivo normal
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)
                # Remove a subpasta e seu conteúdo se for uma pasta
                elif os.path.isdir(caminho_arquivo):
                    apagar_conteudo_pasta(caminho_arquivo)
            print(f"Conteúdo da pasta '{pasta}' apagado com sucesso.")
        else:
            print(f"A pasta '{pasta}' não existe.")
    except Exception as e:
        print(f"Ocorreu um erro ao tentar apagar o conteúdo da pasta '{pasta}': {e}")
                    
def criar_pasta_arquivos():
    pasta_arquivos = "arquivos"
    if not os.path.exists(pasta_arquivos):
        os.makedirs(pasta_arquivos)
        print(f"A pasta '{pasta_arquivos}' foi criada com sucesso.")
    else:
        print(f"A pasta '{pasta_arquivos}' já existe.")

def main():
    # Separar mesas e vincular códigos
    if analise.numeroJogadores() < 3:
        print("="*100)
        print("Todos os jogadores estão em uma partida ou não há jogadores o suficiente para uma nova mesa. (Mínimo 3)")
    else:
        analise.criar_mesa_e_vincular_codigos(
            analise.sortear_mesas(
                analise.numeroJogadores(),
                analise.get_codigo_ids()
            )
        )
    print("="*100)
    
    lista_id_mesa = analise.criar_pastas_mesas_ativas()
    
    if lista_id_mesa:
        print("Pastas das mesas ativas criadas com sucesso!")
        print("="*100)
        
        lista_id_arquivo = analise.consultar_arquivo_e_id_mesas()
        
        criar_pasta_arquivos()
        print("="*100)
        
        apagar_conteudo_pasta("arquivos")
        print("="*100)
        
        arquivos = []
        for lista in lista_id_arquivo:
            arquivos.append(lista[0])
            
        analise.download_from_s3(arquivos)
        
        analise.dividir_codigo_mesas(lista_id_arquivo)
        print("="*100)
        print("Arquivos movidos com sucesso!")
        
        for id_mesa in lista_id_mesa:
            analise.mover_arquivos(id_mesa)
            analise.alterar_status_mesa(id_mesa)
    else:
        print("Não existem mesas ativas no momento.")
    
main()