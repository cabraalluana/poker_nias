import os
import django
import schedule

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise
import time as tm
from datetime import time, timedelta, datetime

def delete_files_in_folder(folder_path):
    
    # Lista os arquivos na pasta
    files = os.listdir(folder_path)
    # Verifica se a lista de arquivos está vazia
    if not files:
        print(f"Pasta {folder_path} está vazia")
    else:
        # Itera sobre os arquivos na pasta
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # Verifica se o caminho é um arquivo regular
            if os.path.isfile(file_path):
                try:
                    # Exclui o arquivo
                    os.remove(file_path)
                    print(f"Arquivo '{filename}' excluído com sucesso.")
                except Exception as e:
                    print(f"Erro ao excluir o arquivo '{filename}': {e}")
                    
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
        
        arquivos = []
        for lista in lista_id_arquivo:
            arquivos.append(lista[0])
            
        analise.download_from_s3(arquivos)
        
        analise.dividir_codigo_mesas(lista_id_arquivo)
        print("="*100)
        print("Arquivos movidos com sucesso!")
        
        for id_mesa in lista_id_mesa:
            analise.alterar_status_mesa(id_mesa)
    else:
        print("Não existem mesas ativas no momento.")
    
schedule.every().day.at("18:00").do(main)

while True:
    schedule.run_pending()
    tm.sleep(1)