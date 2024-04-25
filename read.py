import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise

def main():
    # Loop da área de mesas
    while True:
        print("=====================================================================")
        print("Área das mesas")
        print("1 - Separar mesas;")
        print("2 - Listar mesas ativas;")
        print("3 - Listar mesas inativas;")
        print("4 - Rodar mesas ativas;")
        print("0 - Sair da área das mesas.")
        
        # Solicitar a escolha da área de mesas
        escolha = int(input("Escolha uma opção: "))

        # Realizar ações com base na escolha
        if escolha == 1:
            # Separar mesas e vincular códigos
            if analise.numeroJogadores() < 3:
                print("=====================================================================")
                print("Todos os jogadores estão em uma partida ou não há jogadores o suficiente para uma nova mesa. (Mínimo 3)")
            else:
                res = analise.sortear_mesas(analise.numeroJogadores(), analise.get_codigo_ids())
                analise.criar_mesa_e_vincular_codigos(res)
        elif escolha == 0:
            break
        else:
            print("=====================================================================")
            print("Escolha uma opção válida")
            
# Iniciar o programa
if __name__ == '__main__':
    main()