from django.shortcuts import render, get_object_or_404, redirect
from apps.galeria.models import Fotografia
from django.contrib import messages
from apps.galeria.forms import FotografiaForms

def index(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')
    
    fotografias = Fotografia.objects.filter(publicada=True)

    return render(request, 'galeria/index.html', {"cards": fotografias})

def imagem(request, foto_id):
    fotografia = get_object_or_404(Fotografia, pk=foto_id)

    return render(request, 'galeria/imagem.html', {"fotografia": fotografia})

def nova_imagem(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')
    
    form = FotografiaForms
    
    if request.method == 'POST':
        form = FotografiaForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nova Fotografia cadastrada!')
    
    return render (request, 'galeria/nova_imagem.html', {'form': form})

def editar_imagem(request):
    pass

def deletar_imagem(request):
    pass