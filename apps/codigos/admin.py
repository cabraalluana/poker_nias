from django.contrib import admin
from apps.codigos.models import Codigo

class ListandoCodigo(admin.ModelAdmin):
    list_display = ("id", "arquivo", "usuario")
    list_display_links = ("id", "arquivo")
    search_fields = ("usuario", )
    list_per_page = 10
    
admin.site.register(Codigo, ListandoCodigo)