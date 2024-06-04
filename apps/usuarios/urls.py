from django.urls import path
from apps.usuarios.views import login, cadastro, logout, user_profile, editar_usuario, deletar_usuario

urlpatterns = [
    path('login', login, name='login'),
    path('cadastro', cadastro, name='cadastro'),
    path('logout', logout, name='logout'),
    path('profile', user_profile, name='user_profile'),
    path('editar_usuario/<int:user_id>', editar_usuario, name='editar_usuario'),
    path('deletar_usuario/<int:user_id>', deletar_usuario, name='deletar_usuario'),
]