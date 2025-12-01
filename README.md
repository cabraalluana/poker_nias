# NIAS-IA Poker Challenge

Este é um guia para configurar e executar o projeto **NIAS-IA Poker Challenge** em sua máquina local. Certifique-se de seguir cada passo cuidadosamente para garantir uma configuração adequada.

## 📋 Pré-requisitos

* **Python 3.11+** instalado em sua máquina. [Baixar Python](https://www.python.org/downloads/).
* **Git** instalado.
* **MATLAB** instalado (necessário para a execução da API de competição).

---

## 🚀 Instalação e Configuração

### 1. Clonar o Repositório

Abra o terminal na pasta onde deseja salvar o projeto e execute o comando abaixo (substitua `<link_do_repositório>` pela URL do seu repositório):

```bash
git clone <link_do_repositório>
````

### 2\. Configuração do Ambiente Virtual (.venv)

Abra o terminal na pasta do projeto e crie o ambiente virtual.

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

> **Nota:** Se houver erro de permissão no Windows, execute o comando abaixo e tente ativar novamente:
> `Set-ExecutionPolicy RemoteSigned -Scope Process`

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3\. Instalação de Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

-----

## ⚙️ Configuração Adicional (.env)

Para que o sistema funcione corretamente (especialmente o upload de arquivos para a AWS), é **obrigatório** configurar as variáveis de ambiente.

1.  Crie um arquivo chamado **`.env`** na raiz do projeto (na mesma pasta do `manage.py`).
2.  Adicione o seguinte conteúdo ao arquivo, substituindo os valores pelos fornecidos pelo administrador:

<!-- end list -->

```ini
# Configurações do Django
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=True

# Configurações da AWS
AWS_ACCESS_KEY_ID=seu_access_key_id
AWS_SECRET_ACCESS_KEY=seu_secret_access_key
AWS_STORAGE_BUCKET_NAME=nome_do_seu_bucket
```

-----

## 🗄️ Configuração do Banco de Dados

Crie as tabelas no banco de dados e um usuário administrador.

```bash
# 1. Criar as migrações
python manage.py makemigrations

# 2. Aplicar as migrações ao banco
python manage.py migrate

# 3. Criar superusuário (siga as instruções na tela)
python manage.py createsuperuser
```

-----

## ▶️ Execução do Sistema

Para o sistema funcionar, você precisa rodar dois processos em terminais separados.

### Terminal 1: Servidor Web (Django)

```bash
python manage.py runserver
```

Acesse o site em: **https://www.google.com/search?q=http://127.0.0.1:8000**

### Terminal 2: API do MATLAB

Mantenha este terminal aberto para processar as competições:

```bash
python matlab_api_server.py
```

-----

## 🐳 Rodando com Docker

Se preferir usar Docker e não quiser configurar o Python manualmente:

1.  Crie o arquivo `.env` como explicado acima.
2.  Execute:

<!-- end list -->

```bash
docker-compose up --build
```
