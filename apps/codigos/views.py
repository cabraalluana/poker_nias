from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.codigos.forms import CodigoForms
from apps.codigos.models import Codigo
from django.http import HttpResponse
import mimetypes
import csv

def enviar_codigo(request, user_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')
    
    # Check if a Codigo object exists for the provided user_id
    codigo_exists = Codigo.objects.filter(usuario_id=user_id).exists()

    if codigo_exists:
        codigo = Codigo.objects.get(usuario_id=user_id)
        form = CodigoForms(instance=codigo)
        
        if request.method == 'POST':
            form = CodigoForms(request.POST, request.FILES, instance=codigo)
            if form.is_valid():
                form.save()
                messages.success(request, 'Novo codigo enviado com sucesso!')
                return redirect('index')
    else:
        form = CodigoForms
    
        if request.method == 'POST':
            form = CodigoForms(request.POST, request.FILES)
            if form.is_valid():
                deletar_codigo(request, user_id)
                instance = form.save(commit=False)
                instance.usuario = request.user
                instance.save()
                messages.success(request, 'Código enviado com sucesso!')
                return redirect('index')
            
    codigo = Codigo.objects.filter(usuario=request.user)
            
    return render(request, 'codigos/enviar-codigo.html', {'form': form, 'cards': codigo})

def lista_codigos(request, codigo_id):
    codigo = get_object_or_404(Codigo, pk=codigo_id)
    
    return render(request, 'codigos/lista-codigos.html', {"codigo": codigo})

def index_codigo(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        return redirect('login')
    
    codigos = Codigo.objects.filter(usuario=request.user)
    
    return render(request, 'codigos/index-codigo.html', {"cards": codigos})

def download_codigo(request, codigo_id):
    objeto = Codigo.objects.get(pk=codigo_id)

    # Abrir o arquivo e ler seu conteúdo
    with objeto.arquivo.open(mode='rb') as arquivo:
        response = HttpResponse(arquivo.read(), content_type=mimetypes.guess_type(objeto.arquivo.name)[0])
        response['Content-Disposition'] = f'attachment; filename="{objeto.arquivo.name}"'
        return response
    
def deletar_codigo(request, user_id):
    Codigo.objects.filter(usuario_id=user_id).delete()
    
import csv
from django.shortcuts import render

def upload_csv(request):
    file_path = 'resultados.csv'
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]

    return render(request, 'codigos/index-codigo.html', {'data': data})