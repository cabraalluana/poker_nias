#!/bin/sh
# entrypoint.sh

# Aplica todas as migrações
echo "Aplicando migrações..."
python manage.py migrate

# Roda o servidor Django
echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000
