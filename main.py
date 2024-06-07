import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from src import analise, op

def main():
    if analise.verificar_codigos():
        print("="*100)
        print("Todos os jogadores estão em uma partida.")
    else:
        # Separar mesas e vincular códigos
        if analise.numeroJogadores() < 3:
            print("="*100)
            print("Não há jogadores o suficiente para uma nova mesa. (Mínimo 3)")
        else:
            analise.criar_mesa_e_vincular_codigos(
                analise.sortear_mesas(
                    analise.numeroJogadores(),
                    analise.get_codigo_ids()
                )
            )
    print("="*100)
    
    lista_id_mesa = analise.criar_pastas_mesas_ativas()
    
    if lista_id_mesa:
        print("Pastas das mesas ativas criadas com sucesso!")
        print("="*100)
        
        lista_id_arquivo = analise.consultar_arquivo_e_id_mesas()
        
        op.criar_pasta_arquivos()
        print("="*100)
        
        op.apagar_conteudo_pasta("arquivos")
        print("="*100)
        
        arquivos = []
        for lista in lista_id_arquivo:
            arquivos.append(lista[0])
            
        analise.download_from_s3(arquivos)
        
        analise.dividir_codigo_mesas(lista_id_arquivo)
        print("="*100)
        print("Arquivos movidos com sucesso!")
        
        for id_mesa in lista_id_mesa:
            analise.mover_arquivos(id_mesa)
            
            analise.alterar_status_mesa(id_mesa)
    else:
        print("Não existem mesas ativas no momento.")
    
main()