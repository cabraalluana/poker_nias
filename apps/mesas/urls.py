from django.urls import path
from .views import UltimoTorneioAPI, DispararTorneioAPI

urlpatterns = [
    # Endpoints da API
    path('api/torneio/status/', UltimoTorneioAPI.as_view(), name='api-torneio-status'),
    path('api/torneio/trigger/', DispararTorneioAPI.as_view(), name='api-torneio-trigger'),
]