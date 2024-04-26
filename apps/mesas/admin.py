from django.contrib import admin
from apps.mesas.models import Mesa, Codigo_Mesa

class ListandoMesa(admin.ModelAdmin):
    list_display = ("id", "status")
    list_display_links = ("id", "status")
    search_fields = ("status", )
    list_per_page = 10

class ListandoCodigoMesa(admin.ModelAdmin):
    list_display = ("id", "codigo_id", "mesa_id")
    list_display_links = ("id", "codigo_id", "mesa_id")
    search_fields = ("mesa_id", )
    list_per_page = 10

admin.site.register(Mesa, ListandoMesa)
admin.site.register(Codigo_Mesa, ListandoCodigoMesa)