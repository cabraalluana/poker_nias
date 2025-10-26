from django.shortcuts import render, redirect, get_object_or_404
from apps.usuarios.forms import LoginForms, CadastroForms, EditarForms, EditarSenhaForm
from django.contrib.auth.models import User
from django.contrib import auth, messages
from apps.codigos.models import Codigo
from apps.mesas.models import Codigo_Mesa

def login(request):
    """
    Processa os pedidos para a página de login.
    """
    if request.method == 'POST':
        form = LoginForms(request.POST)

        if form.is_valid():
            nome_usuario = form.cleaned_data.get('usuario')
            senha = form.cleaned_data.get('senha')

            usuario = auth.authenticate(
                request,
                username=nome_usuario,
                password=senha
            )

            if usuario is not None:
                auth.login(request, usuario)
                
                # --- LÓGICA DA MENSAGEM ATUALIZADA ---
                # Verifica se o usuário tem um primeiro nome cadastrado
                if usuario.first_name:
                    # Usa o nome completo (primeiro e último nome)
                    nome_boas_vindas = f"{usuario.first_name} {usuario.last_name}".strip()
                else:
                    # Se não tiver, usa o nome de usuário como alternativa
                    nome_boas_vindas = usuario.username
                
                messages.success(request, f'Bem-vindo(a), {nome_boas_vindas}!')
                return redirect('index')
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
                return render(request, "usuarios/login.html", {"form": form})
    else:
        form = LoginForms()

    return render(request, "usuarios/login.html", {"form": form})

def cadastro(request):
    """
    Processa os pedidos para a página de cadastro da forma correta.
    """
    if request.method == 'POST':
        form = CadastroForms(request.POST)
        
        if form.is_valid():
            # Se o formulário é válido, as validações (email, senhas) já passaram
            nome_usuario = form.cleaned_data.get('usuario')
            primeiro_nome = form.cleaned_data.get('primeiro_nome')
            ultimo_nome = form.cleaned_data.get('ultimo_nome')
            email = form.cleaned_data.get('email')
            senha = form.cleaned_data.get('senha_1')

            # Cria o usuário com os dados já validados
            usuario = User.objects.create_user(
                username=nome_usuario,
                first_name=primeiro_nome,
                last_name=ultimo_nome,
                email=email,
                password=senha
            )
            usuario.save()
            messages.success(request, 'Cadastro efetuado com sucesso!')
            return redirect('login')
        # Se o formulário for inválido, o Django vai renderizar a página com os erros
        
    else:
        form = CadastroForms()

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
            # Atualiza apenas os campos permitidos
            usuario.first_name = form.cleaned_data.get('primeiro_nome')
            usuario.last_name = form.cleaned_data.get('ultimo_nome')
            usuario.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('user_profile')
        
    else:
        # Preenche o formulário com os dados existentes
        form = EditarForms(initial={
            'primeiro_nome': usuario.first_name,
            'ultimo_nome': usuario.last_name,
        })
    
    # Passamos o 'usuario' para o template para mostrar os dados não editáveis
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario, 'user_id': user_id})

def deletar_usuario(request, user_id):
    # Obtém o usuário que será deletado
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Tenta encontrar o código associado a este usuário
    # Usamos .filter() que não gera erro se não encontrar nada
    user_code = Codigo.objects.filter(usuario=user_to_delete).first()
    
    # Se o usuário tiver um código, fazemos as verificações
    if user_code:
        # Verifica se o código está em uma mesa ativa
        is_in_active_mesa = Codigo_Mesa.objects.filter(codigo=user_code, mesa__status=True).exists()
        
        if is_in_active_mesa:
            # Se estiver em uma mesa ativa, impede a exclusão
            messages.error(request, 'Este usuário possui um código em uma competição ativa e não pode ser excluído.')
            return redirect('user_profile') # Redireciona de volta para o perfil
        
    # Se o usuário não tiver código ou se o código não estiver em uma mesa ativa,
    # ele pode ser deletado.
    user_to_delete.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    
    # Se o usuário deletado for o mesmo que está logado, faz o logout
    if request.user.pk is None: # O usuário foi deletado
         auth.logout(request)
         return redirect('login')
         
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
