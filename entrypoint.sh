#!/bin/sh
# entrypoint.sh

# 1. Garante que as pastas necessárias existam
mkdir -p logs tmp

# 2. Aplica as migrações do Django
echo "Aplicando migrações..."
python manage.py migrate

# --- O BLOCO 3 FOI REMOVIDO PARA PARAR O AUTOMÁTICO ---

# 4. Roda o servidor Django (Processo principal)
echo "Iniciando servidor Django na porta 8000..."
python manage.py runserver 0.0.0.0:8000