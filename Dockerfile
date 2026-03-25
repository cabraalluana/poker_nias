FROM python:3.11-slim-bullseye

WORKDIR /app

# Instala apenas o essencial para compilar bibliotecas simples
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instala apenas o que está no seu requirements.txt (NumPy, Pandas, Django, Treys)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# O .dockerignore vai garantir que a pasta .venv não seja copiada!
COPY . .

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]