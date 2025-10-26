import os
# codes/utils_dents.py

import requests # <-- NOVA LÓGICA

def executar_analise_dents(dados_para_analise):
    """
    Esta função recebe dados, chama a API do MATLAB e retorna o resultado.
    """
    api_url = 'http://host.docker.internal:5000/processar'
    dados_para_enviar = {'dados': dados_para_analise}
    resultado_final = None

    print("Contatando a API do MATLAB para análise DEnTS...")
    try:
        response = requests.post(api_url, json=dados_para_enviar)
        response.raise_for_status()  # Lança erro se a resposta não for de sucesso
        resultado_final = response.json()
        print("Análise DEnTS concluída com sucesso via API.")
        
    except requests.exceptions.RequestException as e:
        print(f"Erro de comunicação com a API do MATLAB: {e}")
        # Você pode querer retornar um erro aqui ou um valor padrão
        resultado_final = {'status': 'erro', 'mensagem': str(e)}

    return resultado_final

def get_ultimo_log_dir(base_path=None):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Caminho padrão ajustado para Docker
    if base_path is None:
        base_path = os.path.join(BASE_DIR, 'DEnTS', 'Logs')
        base_path = os.path.abspath(base_path)

    if not os.path.exists(base_path):
        print(f"[ERRO] Pasta base não encontrada: {base_path}")
        return None

    pastas = [os.path.join(base_path, d) for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    if not pastas:
        print("[ERRO] Nenhuma subpasta encontrada em Logs.")
        return None

    ultima = max(pastas, key=os.path.getmtime)
    print(f"[INFO] Última pasta encontrada: {ultima}")
    return ultima

def executar_analise_dents(dados_para_analise):
    """
    Esta função recebe dados, chama a API do MATLAB e retorna o resultado.
    """
    api_url = 'http://host.docker.internal:5000/processar'
    dados_para_enviar = {'dados': dados_para_analise}
    resultado_final = None

    print("Contatando a API do MATLAB para análise DEnTS...")
    try:
        response = requests.post(api_url, json=dados_para_enviar)
        response.raise_for_status()  # Lança erro se a resposta não for de sucesso
        resultado_final = response.json()
        print("Análise DEnTS concluída com sucesso via API.")
        
    except requests.exceptions.RequestException as e:
        print(f"Erro de comunicação com a API do MATLAB: {e}")
        # Você pode querer retornar um erro aqui ou um valor padrão
        resultado_final = {'status': 'erro', 'mensagem': str(e)}

    return resultado_final