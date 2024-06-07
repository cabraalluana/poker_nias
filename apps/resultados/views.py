from django.shortcuts import render

def ranking(request):
		return render(request, 'resultados/ranking.html')