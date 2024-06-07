import os

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