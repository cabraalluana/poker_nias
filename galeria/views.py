from django.shortcuts import render

def index(request):
    dados = {
        1:{"nome": "Regras", "legenda": "Aprenda as regras do Poker."},
        2:{"nome": "Como jogar?", "legenda": "Aprenda a submeter seu código."},
        3:{"nome": "Jogar", "legenda": "Acesse sua conta ou faça um cadastro."},
        4:{"nome": "Ranking", "legenda": "Ranking de Poker - Ganhos e Perdas."}
    }

    return render(request, 'galeria/index.html', {"cards": dados})

def imagem(request):
    return render(request, 'galeria/imagem.html')