# 1️⃣ Imagem base
FROM python:3.11-bullseye

# 2️⃣ Diretório de trabalho
WORKDIR /app

# 3️⃣ Copia o requirements.txt primeiro para otimizar o cache do Docker
COPY requirements.txt .

# 4️⃣ Atualiza pip, etc.
RUN pip install --upgrade pip setuptools wheel

# 5️⃣ Instala dependências do sistema que você já tinha
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# --- SEÇÃO DO MATLAB REMOVIDA ---
# A linha "COPY matlab /usr/local/lib/python3.11/site-packages/matlab"
# foi apagada. Não precisamos mais dela.
# --------------------------------

# 6️⃣ Instala PyQt5 e reportlab
RUN pip install PyQt5==5.15.9 PyQt5-sip==12.11.1 reportlab==4.0

# 7️⃣ Instala o restante das dependências do requirements.txt (agora incluindo 'requests')
RUN pip install --no-cache-dir -r requirements.txt

# 8️⃣ Copia o resto dos arquivos do projeto
COPY . .

# 9️⃣ Expõe a porta 8000
EXPOSE 8000

# 🔟 Copia e torna o entrypoint executável
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 1️⃣1️⃣ Executa o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Define o nome padrão do container
LABEL com.docker.compose.service="poker_nias"