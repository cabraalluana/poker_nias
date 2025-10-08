# 1️⃣ Imagem base
FROM python:3.11-bullseye

# 2️⃣ Diretório de trabalho
WORKDIR /app

# 3️⃣ Copia arquivos do projeto
COPY . /app

# 4️⃣ Atualiza pip, setuptools e wheel
RUN pip install --upgrade pip setuptools wheel

# 5️⃣ Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# 6️⃣ Instala PyQt5 e reportlab
RUN pip install PyQt5==5.15.9 PyQt5-sip==12.11.1 reportlab==4.0

# 7️⃣ Instala o restante das dependências
RUN pip install --no-cache-dir -r requirements.txt

# 8️⃣ Expõe a porta 8000
EXPOSE 8000

# 9️⃣ Copia o entrypoint e torna executável
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 🔟 Executa o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
