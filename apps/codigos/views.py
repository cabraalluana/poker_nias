# Ficheiro: apps/codigos/views.py

from apps.mesas.models import Torneio, HistoricoPartida
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .forms import CodigoForms
from .models import Codigo
from codes.utils_dents import get_ultimo_log_dir
import mimetypes
import os

def index_codigo(request):
    """
    Versão atualizada: Busca os resultados do banco de dados em vez do CSV.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')

    # Busca o último torneio realizado
    ultimo_torneio = Torneio.objects.last()
    partidas = []
    
    if ultimo_torneio:
        # Busca todas as mesas/partidas desse torneio
        partidas = HistoricoPartida.objects.filter(torneio=ultimo_torneio).order_by('fase', 'mesa_id_original')
    else:
        messages.warning(request, "Nenhum torneio foi encontrado no sistema.")

    return render(request, 'codigos/index-codigo.html', {
        'torneio': ultimo_torneio,
        'partidas': partidas,
        'settings': settings
    })

def sobre(request):
    # Ajustado para o caminho correto dentro de templates/shared/
    return render(request, 'shared/sobre.html')

def exibir_resultados(request):
    # Se você quiser que a URL /resultados/ faça o mesmo que index-codigo
    return index_codigo(request)

def enviar_codigo(request, user_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')
    
    if request.user.id != user_id:
         messages.error(request, 'Ação não permitida.')
         return redirect('index')

    codigo_instance = Codigo.objects.filter(usuario_id=user_id).first()

    if request.method == 'POST':
        form = CodigoForms(request.POST, request.FILES, instance=codigo_instance)
        
        if form.is_valid():
            try:
                instance = form.save(commit=False)
                instance.usuario = request.user
                
                # O motor do Django já salva o .py na pasta local /media automaticamente 
                # (já que removemos o S3 do settings.py)
                instance.save() 

                messages.success(request, 'Código do bot (Python) enviado e salvo localmente com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao processar arquivo: {str(e)}')
            
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
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(objeto.arquivo.name)}"'
        return response
    
def deletar_codigo(request, user_id):
    Codigo.objects.filter(usuario_id=user_id).delete()
    messages.success(request, 'Código deletado com sucesso.')
    return redirect('enviar_codigo', user_id=request.user.id)

def detalhes_partida(request, partida_id):
    partida = HistoricoPartida.objects.get(id=partida_id)
    ranking_final = []

    if partida.log_arquivo:
        # CORREÇÃO AQUI: Agora lemos o ficheiro de logs diretamente da pasta local do Docker
        # em vez de buscar da AWS S3
        caminho_local = os.path.join(settings.BASE_DIR, partida.log_arquivo)
        
        if os.path.exists(caminho_local):
            with open(caminho_local, 'r', encoding='utf-8') as f:
                conteudo = f.read().splitlines()

            if conteudo:
                ultima_linha = conteudo[-1].strip().split()
                # Stacks começam no índice 5 (T M A B P ...)
                fichas_finais = [float(f) for f in ultima_linha[5:]]

                # Buscamos os vínculos da mesa para identificar os donos
                from apps.mesas.models import Codigo_Mesa
                vinculos = Codigo_Mesa.objects.filter(mesa_id=partida.mesa_id_original)
                
                for i, v in enumerate(vinculos):
                    usuario = v.codigo.usuario 
                    # Pega o nome completo se existir, senão usa o username
                    nome_competidor = usuario.get_full_name() if usuario.get_full_name() else usuario.username
                    
                    pontuacao = fichas_finais[i] if i < len(fichas_finais) else 0.0
                    ranking_final.append({'nome': nome_competidor, 'pontos': pontuacao})

                # Ordena pelo maior stack
                ranking_final = sorted(ranking_final, key=lambda x: x['pontos'], reverse=True)

    return render(request, 'codigos/detalhes.html', {
        'partida': partida,
        'ranking': ranking_final
    })

def regras_jogo(request):
    return render(request, 'shared/regras.html')

def como_funciona(request):
    return render(request, 'shared/funcionamento.html')

def o_que_e_permitido(request):
    return render(request, 'shared/permitido.html')