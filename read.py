import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise

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

def main():
    # Loop da área de mesas
    while True:
        print("="*100)
        print("Área das mesas")
        print("1 - Separar mesas;")
        print("2 - Listar mesas ativas;")
        print("3 - Listar mesas inativas;")
        print("4 - Rodar mesas ativas;")
        print("0 - Sair da área das mesas.")
        
        # Solicitar a escolha da área de mesas
        escolha = int(input("Escolha uma opção: "))

        # Realizar ações com base na escolha
        if escolha == 1:
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
        elif escolha == 2:
            print("="*100)
            analise.consultar_mesas_e_codigos(analise.obter_id_mesas(True), True)
        elif escolha == 3:
            print("="*100)
            analise.consultar_mesas_e_codigos(analise.obter_id_mesas(False), False)
        elif escolha == 4:
            print("="*100)
            lista_id_mesa = analise.criar_pastas_mesas_ativas()
            if lista_id_mesa:
                print("Pastas das mesas ativas criadas com sucesso!")
                print("="*100)
                
                lista_id_arquivo = analise.consultar_arquivo_e_id_mesas()
                
                delete_files_in_folder("arquivos")
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
            """
                # Chamando a função para modificar o dataframe
                for id_mesa in ids_mesa:
                    df_resultados = resultados.resultado_mesa(resultados.ler_csv_para_dataframe(), mesas.mover_arquivos(id_mesa))
                    mesas.alterar_status_mesa(id_mesa)
                    resultados.salvar_resultado(df_resultados, id_mesa)
            """
        elif escolha == 0:
            break
        else:
            print("="*100)
            print("Escolha uma opção válida")
            
# Iniciar o programa
if __name__ == '__main__':
    main()