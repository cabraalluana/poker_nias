# Ficheiro: apps/codigos/views.py

from apps.mesas.models import Torneio, HistoricoPartida
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from dents.engine import simular_partida
from .forms import CodigoForms
from .models import Codigo
from codes.utils_dents import get_ultimo_log_dir
from apps.mesas.models import Codigo_Mesa
import mimetypes
import os
import shutil
import multiprocessing

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

def testar_bot(request, user_id):
    """
    Modo Teste (Arena de Treino):
    Pega no bot ativo do utilizador, junta-o com os baseline_bots e executa uma partida de 5 segundos.
    """
    if not request.user.is_authenticated or request.user.id != user_id:
        messages.error(request, 'Ação não permitida.')
        return redirect('index')

    codigo_aluno = Codigo.objects.filter(usuario_id=user_id).first()
    if not codigo_aluno:
        messages.error(request, 'Tens de enviar um bot primeiro para poder testá-lo!')
        return redirect('enviar_codigo', user_id=user_id)

    try:
        # 1. Preparar o ambiente da Arena
        pasta_arena = os.path.join(settings.BASE_DIR, 'media', 'arena_treino', f'user_{user_id}')
        os.makedirs(pasta_arena, exist_ok=True)

        # 2. Copiar o bot do aluno para a Arena
        caminho_bot_aluno = os.path.join(settings.BASE_DIR, 'media', codigo_aluno.arquivo.name)
        bot_aluno_arena = os.path.join(pasta_arena, f'aluno_{user_id}.py')
        shutil.copy2(caminho_bot_aluno, bot_aluno_arena)

        # 3. Trazer os "Bots da Casa" para a Arena
        pasta_baseline = os.path.join(settings.BASE_DIR, 'baseline_bots')
        bots_casa = ['bot_passivo.py', 'bot_agressivo.py', 'bot_caotico.py']
        caminhos_jogadores = [bot_aluno_arena]

        for bot in bots_casa:
            origem = os.path.join(pasta_baseline, bot)
            if os.path.exists(origem):
                destino = os.path.join(pasta_arena, bot)
                shutil.copy2(origem, destino)
                caminhos_jogadores.append(destino)

        # 4. Configurar a máquina de simulação
        pasta_logs = os.path.join(pasta_arena, 'logs')
        os.makedirs(pasta_logs, exist_ok=True)

        config = {
            "id_mesa": 999, # ID fictício exclusivo para a Arena
            "jogadores": caminhos_jogadores,
            "numTorneios": 10,
            "pasta_logs": pasta_logs,
            "modo_teste": True
        }

        # 5. Largar a Sandbox de testes (O Combate)
        proc = multiprocessing.Process(target=simular_partida, args=(config,))
        proc.start()
        proc.join(timeout=5) # 5 segundos de tolerância máxima!

        # 6. O Veredicto da Simulação
        if proc.is_alive():
            proc.terminate()
            proc.join()
            messages.error(request, '🚨 O teu bot demorou demasiado tempo a responder (Loop Infinito ou lentidão matemática). Foi desqualificado!')
        elif proc.exitcode != 0:
            messages.error(request, '❌ O teu bot teve um erro de código (Sintaxe, divisão por zero ou variável inexistente) e quebrou.')
        else:
            messages.success(request, '✅ Parabéns! O teu bot sobreviveu à Arena de Treino contra os 3 Bots da Casa sem apresentar erros na execução.')

        # Limpar a arena após o combate para poupar disco
        shutil.rmtree(pasta_arena, ignore_errors=True)

    except Exception as e:
        messages.error(request, f'Ocorreu um erro interno na Arena de Treino: {str(e)}')

    # Regressa ao ecrã do aluno com a resposta
    return redirect('enviar_codigo', user_id=user_id)