import subprocess

def download_from_s3(file_list):
    for file_name in file_list:
        s3_path = f"s3://fotografias-poker/static/{file_name}"
        subprocess.run(["aws", "s3", "cp", s3_path, "arquivos"])

# Exemplo de uso
file_list = ["arquivos/image_1.pdf", "arquivos/Captura_de_tela_de_2024-03-28_15-05-51.png", "arquivos/teste.zip"]  # Lista de nomes de arquivos
download_from_s3(file_list)
