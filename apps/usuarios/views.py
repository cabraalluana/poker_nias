from django.shortcuts import render, redirect, get_object_or_404
from apps.usuarios.forms import LoginForms, CadastroForms, EditarForms, EditarSenhaForm
from django.contrib.auth.models import User
from django.contrib import auth, messages
from apps.codigos.models import Codigo
from apps.mesas.models import Codigo_Mesa

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
            messages.success(request, 'Cadastro efetuado com sucesso!')

            return redirect('login')

    return render(request, 'usuarios/cadastro.html', {"form": form})

def logout(request):
    auth.logout(request)
    messages.success(request, "Logout efetuado com sucessor!")

    return redirect('login')

def user_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Usuário não logado.')
        
        return redirect('login')
    
    user = request.user
    
    return render(request, 'usuarios/user_profile.html', {'user': user})

def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = EditarForms(request.POST)
        
        if form.is_valid():
            # Atualize os campos do usuário manualmente
            usuario.username = form.cleaned_data['usuario']
            usuario.first_name = form.cleaned_data['primeiro_nome']
            usuario.last_name = form.cleaned_data['ultimo_nome']
            usuario.email = form.cleaned_data['email']
            
            usuario.save()
            messages.success(request, 'Usuário editado com sucesso!')
            
            auth.login(request, usuario)
            
            return redirect('user_profile')  # Redirecione para a página de perfil do usuário após a edição
    else:
        # Preencha o formulário com os dados atuais do usuário
        form = EditarForms(initial={
            'usuario': usuario.username,
            'primeiro_nome': usuario.first_name,
            'ultimo_nome': usuario.last_name,
            'email': usuario.email,
        })
    
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'user_id': user_id})

def deletar_usuario(request, user_id):
    user = User.objects.get(id=user_id)
    code = Codigo.objects.get(usuario=user)
    has_active_code = Codigo_Mesa.objects.filter(codigo=code).exists()
    
    if has_active_code:
        # Verifica se o código está em uma mesa com status True
        has_active_code_in_active_mesa = Codigo_Mesa.objects.filter(codigo=code, mesa__status=True).exists()
        if has_active_code_in_active_mesa == False:
            user.delete()
            messages.success(request, 'Usuário excluído com sucesso!')
        else:
            messages.error(request, 'Este usuário possui um código ativo em uma mesa com status inativo e não pode ser excluído.')
    else:
        user.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
    
    return redirect('index')

def editar_senha(request):
    if request.method == 'POST':
        form = EditarSenhaForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('user_profile')  # Redireciona para o perfil do usuário após a edição da senha
    else:
        form = EditarSenhaForm(request.user)
    return render(request, 'usuarios/editar_senha.html', {'form': form})
