from django.urls import path
from apps.resultados.views import ranking

urlpatterns = [
    path('ranking', ranking, name='ranking'),
]