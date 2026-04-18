# NIAS-IA: Plataforma de Competição e Aprendizado em IA
Este projeto é um ecossistema de simulação de Poker desenvolvido como Trabalho de Conclusão de Curso (TCC) em Engenharia Elétrica na UFV. O objetivo é facilitar o ensino de Inteligência Computacional através de um ambiente competitivo onde alunos desenvolvem agentes (bots) para disputar torneios em um ambiente seguro e controlado.

## 🛠️ Tecnologias e Arquitetura
Framework: Django (Python 3.11+)

Banco de Dados: PostgreSQL (via Docker)

Orquestração: Docker & Docker Compose

Storage de Logs: Amazon S3 (Boto3)

Segurança: Sandbox com restrição de módulos (AST) e multiprocessamento.

Integração: Compatibilidade com algoritmos de tomada de decisão e MATLAB.

## 🚀 Configuração Rápida (Via Docker)
A forma recomendada de executar o projeto é via Docker, garantindo que todas as dependências (inclusive o banco de dados) subam corretamente.

1. Clonar o Repositório
Bash
git clone https://github.com/cabraalluana/poker_nias.git
cd poker_nias
2. Configurar Variáveis de Ambiente (.env)
Crie um arquivo .env na raiz do projeto e preencha com suas credenciais. Este passo é obrigatório para que os logs no S3 funcionem.
3. Subir o Ambiente
Bash
docker-compose up --build -d
O site estará disponível em http://localhost:8000.

## 🏆 Executando um Torneio
Diferente de um site comum, o NIAS-IA possui um orquestrador que processa as partidas. Após os alunos fazerem o upload dos códigos via interface, você deve disparar o torneio:

Bash
# Entrar no container web e rodar o orquestrador
docker exec -it poker_nias-web-1 python read.py
Este comando irá:

Buscar os códigos no banco de dados.

Validar a segurança (Sandbox).

Simular as mesas de Poker.

Exportar os rankings e logs detalhados para o Amazon S3.

## 📂 Estrutura de Páginas
O sistema foi desenhado para ser uma ferramenta didática completa:

Home: Dashboard de boas-vindas.

Sobre: Fundamentação teórica do projeto (Baseada no artigo COBENGE 2024).

Regras: Lógica do Poker simplificado para os desenvolvedores de bots.

Funcionamento: Detalhes da infraestrutura (Docker + S3 + Sandbox).

Resultados: Ranking dinâmico extraído diretamente do banco de dados e logs da AWS.

## 🛡️ Segurança e Sandbox
Para proteger o servidor de códigos maliciosos, o NIAS-IA utiliza uma camada de proteção que:

Bloqueia import os, sys, subprocess e chamadas de rede.

Permite apenas bibliotecas de cálculo como numpy, math e random.

Executa cada bot em um processo isolado com tempo de resposta limitado (Timeout).

## 🎓 Créditos e TCC
Desenvolvido por Luana Cabral Orientador: Rodolpho Vilela Alves Neves

Universidade Federal de Viçosa (UFV) Departamento de Engenharia Elétrica
