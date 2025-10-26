# matlab_api_server.py
import matlab.engine
from flask import Flask, request, jsonify

print("Iniciando MATLAB Engine... Isso pode demorar um pouco.")
# Inicia o engine uma vez para ser reutilizado
eng = matlab.engine.start_matlab()
print("MATLAB Engine iniciado com sucesso.")

app = Flask(__name__)

# Cria uma rota/endpoint para receber os pedidos
@app.route('/processar', methods=['POST'])
def processar_dados_endpoint():
    try:
        # Pega os dados JSON enviados pelo seu back-end Django
        dados_recebidos = request.json
        print(f"Dados recebidos para processamento: {dados_recebidos}")

        # Exemplo: Supondo que você está enviando uma lista de números
        # Converta os dados para o formato que sua função MATLAB espera
        dados_para_matlab = matlab.double(dados_recebidos['dados'])

        # --- CHAME A SUA FUNÇÃO MATLAB AQUI ---
        # Substitua 'minha_funcao_tcc' pelo nome real da sua função e ajuste os parâmetros
        # O nargout=2 significa que esperamos 2 resultados de volta
        media_resultado, soma_resultado = eng.minha_funcao_tcc(dados_para_matlab, nargout=2)

        print(f"Resultados do MATLAB: Média={media_resultado}, Soma={soma_resultado}")

        # Retorna o resultado como JSON para o Django
        return jsonify({
            'status': 'sucesso',
            'media': media_resultado,
            'soma': soma_resultado
        })

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(host='0.0.0.0', port=5000)