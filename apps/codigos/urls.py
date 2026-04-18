from django.urls import path
from apps.codigos.views import enviar_codigo, lista_codigos, index_codigo, download_codigo, index_codigo, detalhes_partida, sobre, o_que_e_permitido, como_funciona, regras_jogo

urlpatterns = [
    path('enviar-codigo/<int:user_id>', enviar_codigo, name='enviar_codigo'),
    path('lista-codigos/<int:codigo_id>', lista_codigos, name='lista_codigos'),
    path('index-codigo', index_codigo, name='index_codigo'),
    path('download-codigo/<int:codigo_id>', download_codigo, name='download_codigo'),
    path('partida/<int:partida_id>/', detalhes_partida, name='detalhes_partida'),
    path('sobre/', sobre, name='sobre'),
    path('regras/', regras_jogo, name='regras'),
    path('como-funciona/', como_funciona, name='como_funciona'),
    path('permitido/', o_que_e_permitido, name='permitido'),
]