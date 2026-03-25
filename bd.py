import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Tabelas relacionadas aos usuários
tabelas_usuarios = [
    "auth_user_groups",
    "auth_user_user_permissions",
    "django_admin_log",
    "django_session",
    "auth_user"
]

# Tabelas da sua aplicação
tabelas_app = [
    "codigos_codigo",
    "galeria_fotografia",
    "mesas_mesa",
    "mesas_codigo_mesa"
]

print("Limpando tabelas de usuarios...")
for tabela in tabelas_usuarios:
    print(f"Limpando: {tabela}")
    cursor.execute(f"DELETE FROM {tabela}")

print("\nLimpando tabelas da aplicacao...")
for tabela in tabelas_app:
    print(f"Limpando: {tabela}")
    cursor.execute(f"DELETE FROM {tabela}")

conn.commit()
conn.close()

print("\nLimpeza concluida!")
