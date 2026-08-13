import os
import django
from django.core.files import File

# 1. Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings') 
django.setup()

# 2. Importações
from django.contrib.auth.models import User
from apps.codigos.models import Codigo  # Ajuste isso se a sua model de código estiver em outro lugar

# 3. Mapeamento com Dados Completos de Cadastro
MAPEAMENTO_BOTS = {
    "bot_Amanda_Patricia.py": {
        "username": "amanda.patricia",
        "first_name": "Amanda",
        "last_name": "Patricia",
        "email": "amanda.patricia@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_daniel.py": {
        "username": "daniel.silva",
        "first_name": "Daniel",
        "last_name": "Silva",
        "email": "daniel.silva@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_daniel_2.py": {
        "username": "daniel.costa",
        "first_name": "Daniel",
        "last_name": "Costa",
        "email": "daniel.costa@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_daniel_2_rna.py": {
        "username": "daniel.oliveira",
        "first_name": "Daniel",
        "last_name": "Oliveira",
        "email": "daniel.oliveira@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_daniel_rna.py": {
        "username": "daniel.santos",
        "first_name": "Daniel",
        "last_name": "Santos",
        "email": "daniel.santos@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_diego.py": {
        "username": "diego.souza",
        "first_name": "Diego",
        "last_name": "Souza",
        "email": "diego.souza@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_diego_rna.py": {
        "username": "diego.martins",
        "first_name": "Diego",
        "last_name": "Martins",
        "email": "diego.martins@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_jose.py": {
        "username": "jose.pereira",
        "first_name": "José",
        "last_name": "Pereira",
        "email": "jose.pereira@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_jose_rna.py": {
        "username": "jose.lima",
        "first_name": "José",
        "last_name": "Lima",
        "email": "jose.lima@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_luana.py": {
        "username": "luana.almeida",
        "first_name": "Luana",
        "last_name": "Almeida",
        "email": "luana.almeida@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_luana_rna.py": {
        "username": "luana.ribeiro",
        "first_name": "Luana",
        "last_name": "Ribeiro",
        "email": "luana.ribeiro@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_pedro.py": {
        "username": "pedro.alves",
        "first_name": "Pedro",
        "last_name": "Alves",
        "email": "pedro.alves@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_pedro_rna.py": {
        "username": "pedro.carvalho",
        "first_name": "Pedro",
        "last_name": "Carvalho",
        "email": "pedro.carvalho@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_rodrigo.py": {
        "username": "rodrigo.ferreira",
        "first_name": "Rodrigo",
        "last_name": "Ferreira",
        "email": "rodrigo.ferreira@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_rodrigo_rna.py": {
        "username": "rodrigo.gomes",
        "first_name": "Rodrigo",
        "last_name": "Gomes",
        "email": "rodrigo.gomes@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_torugo_peluzio.py": {
        "username": "torugo.peluzio",
        "first_name": "Torugo",
        "last_name": "Peluzio",
        "email": "torugo.peluzio@teste.tcc",
        "senha": "Teste@2026"
    },
    "bot_Werikson_Frederiko.py": {
        "username": "werikson.frederiko",
        "first_name": "Wérikson",
        "last_name": "Frederiko",
        "email": "werikson.frederiko@teste.tcc",
        "senha": "Teste@2026"
    }
}

def popular_banco():
    pasta_bots = './bots_teste'
    
    if not os.path.exists(pasta_bots):
        print(f"❌ Pasta '{pasta_bots}' não encontrada. Crie a pasta e coloque os arquivos .py nela.")
        return

    print(f"🚀 Iniciando o CADASTRO COMPLETO e submissão de {len(MAPEAMENTO_BOTS)} bots...")

    for arquivo, dados_usuario in MAPEAMENTO_BOTS.items():
        caminho_arquivo = os.path.join(pasta_bots, arquivo)
        
        # Verifica se o arquivo do bot está lá
        if not os.path.exists(caminho_arquivo):
            print(f"⚠️ AVISO: O arquivo '{arquivo}' não foi encontrado na pasta. Pulando usuário...")
            continue

        # Extrai os dados do dicionário
        username = dados_usuario["username"]
        email = dados_usuario["email"]
        nome = dados_usuario["first_name"]
        sobrenome = dados_usuario["last_name"]
        senha = dados_usuario["senha"]

        # CRIA O USUÁRIO COM TODOS OS DADOS
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': nome,
                'last_name': sobrenome,
            }
        )
        
        # Se o usuário foi criado agora, define a senha
        if created:
            user.set_password(senha)
            user.save()
            print(f"👤 Cadastro Completo: {nome} {sobrenome} ({username})")
        else:
            print(f"ℹ️ Usuário {username} já existia no banco.")
        
        # CRIA A SUBMISSÃO NO BANCO E ANEXA O ARQUIVO
        with open(caminho_arquivo, 'rb') as f:
            # Cria a instância da submissão vinculada ao usuário completo
            nova_submissao = Codigo(usuario=user) 
            
            # O .save() no campo FileField já cuida de mover e renomear
            nova_submissao.arquivo.save(arquivo, File(f))
            nova_submissao.save()
            
        print(f"   ✅ Submissão de '{arquivo}' concluída com sucesso!")
        
    print("\n🎉 Banco populado com sucesso! Seus 17 cadastros completos e bots estão prontos.")

if __name__ == '__main__':
    popular_banco()