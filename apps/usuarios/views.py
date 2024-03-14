from django.shortcuts import render, redirect
from apps.usuarios.forms import LoginForms, CadastroForms
from django.contrib.auth.models import User
from django.contrib import auth, messages

def login(request):
    form = LoginForms()

    if request.method == 'POST':
        form = LoginForms(request.POST)

        if form.is_valid():
            user = form['usuario'].value()
            senha = form['senha'].value()

            usuario = auth.authenticate(
                request,
                username=user,
                password=senha
            )

            if usuario is not None:
                auth.login(request, usuario)
                messages.success(request, f'{user} logado com sucesso!')
                return redirect('index')
            else:
                messages.error(request, 'Erro ao efetuar o login.')
                return redirect('login')

    return render(request, 'usuarios/login.html', {"form": form})

def cadastro(request):
    form = CadastroForms()

    if request.method == 'POST':
        form = CadastroForms(request.POST)
        
        if form.is_valid():
            user = form['usuario'].value()
            primeiro_nome = form['primeiro_nome'].value()
            ultimo_nome = form['ultimo_nome'].value()
            email = form['email'].value()
            senha = form['senha_1'].value()

            if User.objects.filter(username=user).exists():
                messages.error(request, 'Usuário já existente')
                return redirect('cadastro')
            
            usuario = User.objects.create_user(
                username=user,
                first_name=primeiro_nome,
                last_name=ultimo_nome,
                email=email,
                password=senha
            )

            usuario.save()
            messages.success(request, 'Cadastro efetuado com sucesso! ')

            return redirect('login')

    return render(request, 'usuarios/cadastro.html', {"form": form})

def logout(request):
    auth.logout(request)
    messages.success(request, "Logout efetuado com sucessor!")

    return redirect('login')