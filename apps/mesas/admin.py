import subprocess
import sys
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from apps.mesas.models import Mesa, Codigo_Mesa, Torneio, ResultadoTorneio, HistoricoPartida

# --- 1. CONFIGURAÇÕES DE INLINE ---

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
    fields = ('mesa_id_original', 'fase', 'tempo_processamento_ms', 'ver_log_s3')
    readonly_fields = ('mesa_id_original', 'fase', 'tempo_processamento_ms', 'ver_log_s3')
    can_delete = False
    verbose_name = "Mesa Processada"
    verbose_name_plural = "Histórico de Mesas"

    def ver_log_s3(self, obj):
        if obj.log_arquivo:
            # Assume-se que o caminho guardado é o relativo (Key do S3)
            url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj.log_arquivo}"
            return format_html('<a href="{}" target="_blank" style="font-weight: bold;">📄 Abrir Log</a>', url)
        return "N/A"
    ver_log_s3.short_description = "Link AWS"

# --- 2. CONFIGURAÇÃO DO TORNEIO ADMIN ---

class ListandoTorneio(admin.ModelAdmin):
    list_display = ("id", "data_inicio", "quantidade_jogadores", "exibir_duracao", "botao_executar")
    list_display_links = ("id", "data_inicio")
    list_filter = ("data_inicio",)
    inlines = [ResultadoInline, PartidaInline]

    def exibir_duracao(self, obj):
        if obj.tempo_total_ms:
            return f"{obj.tempo_total_ms / 1000:.2f} segundos"
        return "Em execução..."
    exibir_duracao.short_description = "Tempo Total"

    # --- Lógica do Botão de Execução ---
    def botao_executar(self, obj):
        return format_html(
            '<a class="button" href="/admin/mesas/torneio/run/" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">▶ Executar Torneio</a>'
        )
    botao_executar.short_description = "Ações Web"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run/', self.admin_site.admin_view(self.view_executar_torneio)),
        ]
        return custom_urls + urls

    def view_executar_torneio(self, request):
        try:
            # Dispara o read.py em segundo plano usando o interpretador atual
            subprocess.Popen([sys.executable, "read.py"])
            messages.success(request, "🚀 Torneio disparado com sucesso em segundo plano!")
        except Exception as e:
            messages.error(request, f"❌ Falha ao iniciar torneio: {str(e)}")
        return redirect("../")

# --- 3. CONFIGURAÇÕES ADICIONAIS ---

class ListandoHistoricoPartida(admin.ModelAdmin):
    list_display = ("id", "torneio", "fase", "mesa_id_original", "ver_log_clicavel")
    list_filter = ("fase", "torneio")

    def ver_log_clicavel(self, obj):
        if obj.log_arquivo:
            url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj.log_arquivo}"
            return format_html('<a href="{}" target="_blank">🔗 Ver no S3</a>', url)
        return "Sem log"
    ver_log_clicavel.short_description = "Caminho AWS"

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

# --- 4. REGISTOS ---

admin.site.register(Torneio, ListandoTorneio)
admin.site.register(HistoricoPartida, ListandoHistoricoPartida)
admin.site.register(Mesa, ListandoMesa)
admin.site.register(Codigo_Mesa, ListandoCodigoMesa)
admin.site.register(ResultadoTorneio)