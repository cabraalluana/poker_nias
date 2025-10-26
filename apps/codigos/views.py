# Ficheiro: apps/codigos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .forms import CodigoForms
from .models import Codigo
from codes.utils_dents import get_ultimo_log_dir
import mimetypes
import csv
import os

def index_codigo(request):
    """
    Esta view agora encontra o 'resultados.csv' mais recente e exibe seus dados.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')

    data = []
    # 1. Chama a sua função para obter o diretório de log mais recente
    ultimo_log_dir = get_ultimo_log_dir()

    if ultimo_log_dir:
        # 2. Constrói o caminho completo para o arquivo resultados.csv
        file_path = os.path.join(ultimo_log_dir, 'resultados.csv')

        # 3. Verifica se o arquivo realmente existe antes de tentar lê-lo
        if os.path.exists(file_path):
            try:
                # 4. Lê os dados do arquivo CSV
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    # Usamos DictReader para que ele leia o cabeçalho (Jogador, Pontuacao)
                    reader = csv.DictReader(csvfile)
                    # Converte os dados para uma lista de dicionários
                    data = [row for row in reader]
                print(f"[INFO] {len(data)} linhas lidas de {file_path}")
            except Exception as e:
                print(f"[ERRO] Falha ao ler o arquivo CSV: {e}")
                messages.error(request, f"Erro ao processar o arquivo de resultados: {e}")
        else:
            print(f"[AVISO] Arquivo 'resultados.csv' não encontrado em {ultimo_log_dir}")
            messages.warning(request, "A pasta de resultados mais recente não contém um arquivo 'resultados.csv'.")
    else:
        print("[AVISO] Nenhuma pasta de log foi encontrada.")
        messages.warning(request, "Nenhuma pasta de resultados foi encontrada no sistema.")

    # 5. Renderiza o template, passando a lista 'data' (que pode estar vazia)
    return render(request, 'codigos/index-codigo.html', {'data': data})


# --- O RESTO DAS SUAS VIEWS CONTINUAM IGUAIS ---

def enviar_codigo(request, user_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')
    
    codigo_instance = Codigo.objects.filter(usuario_id=user_id).first()

    if request.method == 'POST':
        form = CodigoForms(request.POST, request.FILES, instance=codigo_instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.usuario = request.user
            instance.save()
            messages.success(request, 'Código enviado/atualizado com sucesso!')
            return redirect('enviar_codigo', user_id=request.user.id)
    else:
        form = CodigoForms(instance=codigo_instance)
            
    codigos_ativos = Codigo.objects.filter(usuario=request.user)
            
    return render(request, 'codigos/enviar-codigo.html', {'form': form, 'cards': codigos_ativos})

def lista_codigos(request, codigo_id):
    codigo = get_object_or_404(Codigo, pk=codigo_id)
    return render(request, 'codigos/lista-codigos.html', {"codigo": codigo})

def download_codigo(request, codigo_id):
    objeto = get_object_or_404(Codigo, pk=codigo_id)
    with objeto.arquivo.open(mode='rb') as arquivo:
        response = HttpResponse(arquivo.read(), content_type=mimetypes.guess_type(objeto.arquivo.name)[0])
        response['Content-Disposition'] = f'attachment; filename="{objeto.arquivo.name}"'
        return response
    
def deletar_codigo(request, user_id):
    Codigo.objects.filter(usuario_id=user_id).delete()
    messages.success(request, 'Código deletado com sucesso.')
    return redirect('enviar_codigo', user_id=request.user.id)