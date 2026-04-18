# NIAS-IA: Plataforma de Competição e Aprendizado em IA
Este projeto é um ecossistema de simulação de Poker desenvolvido como Trabalho de Conclusão de Curso (TCC) em Engenharia Elétrica na UFV. O objetivo é facilitar o ensino de Inteligência Computacional através de um ambiente competitivo onde alunos desenvolvem agentes (bots) para disputar torneios em um ambiente seguro e controlado.

## 🛠️ Tecnologias e Arquitetura
Framework: Django (Python 3.11+)

Banco de Dados: PostgreSQL (via Docker)

Orquestração: Docker & Docker Compose

Storage de Logs: Amazon S3 (Boto3)

Segurança: Sandbox com restrição de módulos (AST).

## 🚀 Configuração e Instalação
1. Clonar o Repositório e Configurar Ambiente
```bash
git clone https://github.com/cabraalluana/poker_nias.git
cd poker_nias

# Recomendado: Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

2. Instalar Dependências
```bash
pip install -r requirements.txt
```

3. Configurar Variáveis de Ambiente (.env)
Crie um arquivo .env na raiz do projeto com as configurações que recebeu.

## 🗄️ Configuração do Banco de Dados
Antes de rodar o sistema, é necessário preparar as tabelas no banco de dados:

```bash
# Gerar arquivos de migração
python manage.py makemigrations

# Aplicar as mudanças no banco de dados
python manage.py migrate

# Criar um administrador para o painel
python manage.py createsuperuser
```

## 🐳 Execução via Docker (Recomendado)
Se preferir rodar tudo isolado em containers:

```bash
docker-compose up --build -d
```

O Docker executará as migrações automaticamente conforme configurado no entrypoint.sh.

## 🏆 Executando um Torneio
Para processar as partidas após o upload dos códigos:

```bash
docker exec -it poker_nias-web-1 python read.py
```

## 🎓 Créditos e TCC
Desenvolvido por Luana Oliveira Cabral 

Orientador: Rodolpho Vilela Alves Neves

Universidade Federal de Viçosa (UFV)
