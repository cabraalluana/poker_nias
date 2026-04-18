# Ficheiro: apps/codigos/views.py

from apps.mesas.models import Torneio, HistoricoPartida
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .forms import CodigoForms
from .models import Codigo
from codes.utils_dents import get_ultimo_log_dir
import boto3
import mimetypes
import csv
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
            instance = form.save(commit=False)
            instance.usuario = request.user
            instance.save() # O arquivo ZIP vai para o S3 aqui

            # --- CORREÇÃO AQUI ---
            try:
                # Definir pasta de extração LOCAL (No Container Docker)
                # Mesmo que o zip esteja no S3, vamos extrair os scripts para o disco do container para o MATLAB rodar rápido
                pasta_destino = os.path.join(settings.MEDIA_ROOT, 'codigos_extraidos', f'user_{request.user.id}')
                
                # Limpeza da pasta local
                if os.path.exists(pasta_destino):
                    shutil.rmtree(pasta_destino)
                os.makedirs(pasta_destino)

                # AQUI MUDOU: Abrimos o arquivo como objeto, sem pedir o 'path'
                with instance.arquivo.open('rb') as zip_file_obj:
                    # Verifica se é zip válido
                    if zipfile.is_zipfile(zip_file_obj):
                        # Abre o zip usando o objeto em memória
                        with zipfile.ZipFile(zip_file_obj, 'r') as zip_ref:
                            zip_ref.extractall(pasta_destino)
                        
                        # Verifica main.m
                        if not os.path.exists(os.path.join(pasta_destino, 'main.m')):
                            messages.warning(request, 'Alerta: O arquivo "main.m" não encontrado no ZIP!')
                        
                        # Criar o Wrapper AI1.m (Igual antes)
                        conteudo_wrapper = """function [saida] = AI1(varargin)
    % Wrapper gerado automaticamente
    try
        if nargin > 0
            saida = main(varargin{:});
        else
            saida = main();
        end
    catch e
        rethrow(e);
    end
end
"""
                        with open(os.path.join(pasta_destino, 'AI1.m'), 'w') as f:
                            f.write(conteudo_wrapper)

                        messages.success(request, 'Código enviado e processado com sucesso!')
                    else:
                        messages.error(request, 'O arquivo enviado não é um ZIP válido.')

            except Exception as e:
                # Printa o erro no terminal para ajudar a debugar
                print(f"Erro no processamento do ZIP: {e}")
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
        response['Content-Disposition'] = f'attachment; filename="{objeto.arquivo.name}"'
        return response
    
def deletar_codigo(request, user_id):
    Codigo.objects.filter(usuario_id=user_id).delete()
    messages.success(request, 'Código deletado com sucesso.')
    return redirect('enviar_codigo', user_id=request.user.id)

def detalhes_partida(request, partida_id):
    partida = HistoricoPartida.objects.get(id=partida_id)
    ranking_final = []

    if partida.log_arquivo:
        s3 = boto3.client('s3', 
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=partida.log_arquivo)
        conteudo = obj['Body'].read().decode('utf-8').splitlines()

        if conteudo:
            ultima_linha = conteudo[-1].strip().split()
            # Stacks começam no índice 5 (T M A B P ...)
            fichas_finais = [float(f) for f in ultima_linha[5:]]

            # Buscamos os vínculos da mesa para identificar os donos
            from apps.mesas.models import Codigo_Mesa
            vinculos = Codigo_Mesa.objects.filter(mesa_id=partida.mesa_id_original)
            
            for i, v in enumerate(vinculos):
                # ACESSANDO O USUÁRIO: Se o seu campo for 'user', troque usuario por user
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