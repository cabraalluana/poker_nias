from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from apps.mesas.models import Mesa, Codigo_Mesa, Torneio, ResultadoTorneio, HistoricoPartida

# --- 1. CONFIGURAÇÕES DE INLINE (Visualização dentro do Torneio) ---

class ResultadoInline(admin.TabularInline):
    model = ResultadoTorneio
    extra = 0
    fields = ('posicao', 'codigo', 'fichas_finais')
    readonly_fields = ('posicao', 'codigo', 'fichas_finais')
    can_delete = False
    verbose_name = "Classificação Final"
    verbose_name_plural = "Classificações Finais"

class PartidaInline(admin.TabularInline):
    model = HistoricoPartida
    extra = 0
    # Adicionamos 'ver_log_s3' para ter o link clicável aqui dentro também
    fields = ('mesa_id_original', 'fase', 'tempo_processamento_ms', 'ver_log_s3')
    readonly_fields = ('mesa_id_original', 'fase', 'tempo_processamento_ms', 'ver_log_s3')
    can_delete = False
    verbose_name = "Mesa Processada"
    verbose_name_plural = "Histórico de Mesas"

    def ver_log_s3(self, obj):
        if obj.log_arquivo:
            url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj.log_arquivo}"
            return format_html('<a href="{}" target="_blank">📄 Abrir Log</a>', url)
        return "N/A"
    ver_log_s3.short_description = "Link AWS"

# --- 2. CONFIGURAÇÕES PRINCIPAIS ---

class ListandoTorneio(admin.ModelAdmin):
    list_display = ("id", "data_inicio", "quantidade_jogadores", "exibir_duracao")
    list_display_links = ("id", "data_inicio")
    list_filter = ("data_inicio",)
    
    # O segredo para o TCC: mostra resultados e partidas na mesma tela
    inlines = [ResultadoInline, PartidaInline]

    def exibir_duracao(self, obj):
        if obj.tempo_total_ms:
            return f"{obj.tempo_total_ms / 1000:.2f} segundos"
        return "Pendente..."
    exibir_duracao.short_description = "Tempo de Execução"

class ListandoHistoricoPartida(admin.ModelAdmin):
    list_display = ("id", "torneio", "fase", "mesa_id_original", "ver_log_clicavel")
    list_filter = ("fase", "torneio")

    def ver_log_clicavel(self, obj):
        if obj.log_arquivo:
            url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj.log_arquivo}"
            return format_html('<a href="{}" target="_blank">🔗 Ver no S3</a>', url)
        return "Sem log"
    ver_log_clicavel.short_description = "Caminho AWS"

# --- 3. CLASSES ORIGINAIS (Mantidas para compatibilidade) ---

class ListandoMesa(admin.ModelAdmin):
    list_display = ("id", "status", "torneio")
    list_display_links = ("id", "status")
    search_fields = ("status", )
    list_per_page = 10

class ListandoCodigoMesa(admin.ModelAdmin):
    list_display = ("id", "codigo_id", "mesa_id")
    list_display_links = ("id", "codigo_id", "mesa_id")
    search_fields = ("mesa_id", )
    list_per_page = 10

# --- 4. REGISTOS NO SISTEMA ---

admin.site.register(Torneio, ListandoTorneio)
admin.site.register(ResultadoTorneio) # Pode registar à parte se quiseres ver a lista global
admin.site.register(HistoricoPartida, ListandoHistoricoPartida)
admin.site.register(Mesa, ListandoMesa)
admin.site.register(Codigo_Mesa, ListandoCodigoMesa)