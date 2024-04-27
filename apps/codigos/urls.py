from django.urls import path
from apps.codigos.views import enviar_codigo, lista_codigos, index_codigo, download_codigo

urlpatterns = [
    path('enviar-codigo/<int:user_id>', enviar_codigo, name='enviar_codigo'),
    path('lista-codigos/<int:codigo_id>', lista_codigos, name='lista_codigos'),
    path('index-codigo', index_codigo, name='index_codigo'),
    path('download-codigo/<int:codigo_id>', download_codigo, name='download_codigo')
]