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
    fields = ('mesa_id_original', 'fase', 'status_formatado', 'tempo_processamento_ms', 'ver_log_s3')
    readonly_fields = ('mesa_id_original', 'fase', 'status_formatado', 'tempo_processamento_ms', 'ver_log_s3')
    can_delete = False
    verbose_name = "Mesa Processada"
    verbose_name_plural = "Histórico de Mesas"

    def status_formatado(self, obj):
        colors = {'sucesso': '#28a745', 'timeout': '#ffc107', 'erro_bot': '#dc3545'}
        color = colors.get(obj.status_execucao, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 10px; text-transform: uppercase;">{}</span>',
            color, obj.status_execucao
        )
    status_formatado.short_description = "Status"

    def ver_log_s3(self, obj):
        if obj.log_arquivo:
            url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj.log_arquivo}"
            return format_html('<a href="{}" target="_blank" style="font-weight: bold; color: #007bff;">📄 Abrir Log</a>', url)
        return format_html('<span style="color: #999;">N/A</span>')
    ver_log_s3.short_description = "Link AWS"

# --- 2. CONFIGURAÇÃO DO TORNEIO ADMIN ---

class ListandoTorneio(admin.ModelAdmin):
    list_display = ("id", "data_inicio", "quantidade_jogadores", "exibir_duracao", "botao_executar")
    list_display_links = ("id", "data_inicio")
    list_filter = ("data_inicio",)
    inlines = [ResultadoInline, PartidaInline]

    def exibir_duracao(self, obj):
        if obj.tempo_total_ms:
            return f"{obj.tempo_total_ms / 1000:.2f} s"
        return format_html('<span style="color: #e67e22; font-style: italic;">Processando...</span>')
    exibir_duracao.short_description = "Duração"

    def botao_executar(self, obj):
        return format_html(
            '<a class="button" href="/admin/mesas/torneio/run/" style="background-color: #28a745; color: white; padding: 5px 12px; border-radius: 4px; text-decoration: none; font-weight: bold;">▶ DISPARAR TORNEIO</a>'
        )
    botao_executar.short_description = "Controle Web"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path('run/', self.admin_site.admin_view(self.view_executar_torneio))]
        return custom_urls + urls

    def view_executar_torneio(self, request):
        try:
            subprocess.Popen([sys.executable, "read.py"])
            messages.success(request, "🚀 Motor DEnTS iniciado!")
        except Exception as e:
            messages.error(request, f"❌ Erro ao disparar: {str(e)}")
        return redirect("../")

# --- 3. CONFIGURAÇÕES ADICIONAIS ---

class ListandoHistoricoPartida(admin.ModelAdmin):
    list_display = ("id", "torneio", "fase", "mesa_id_original", "status_formatado", "ver_log_clicavel")
    list_filter = ("status_execucao", "fase", "torneio")

    def status_formatado(self, obj):
        colors = {'sucesso': '#28a745', 'timeout': '#ffc107', 'erro_bot': '#dc3545'}
        color = colors.get(obj.status_execucao, '#6c757d')
        return format_html('<b style="color: {}; text-transform: uppercase;">{}</b>', color, obj.status_execucao)
    status_formatado.short_description = "Status"

    def ver_log_clicavel(self, obj):
        if obj.log_arquivo:
            url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{obj.log_arquivo}"
            return format_html('<a href="{}" target="_blank">🔗 Log S3</a>', url)
        return "Sem log"

class ListandoMesa(admin.ModelAdmin):
    list_display = ("id", "status")

class ListandoCodigoMesa(admin.ModelAdmin):
    list_display = ("id", "codigo_id", "mesa_id")

# --- 4. REGISTROS ---
admin.site.register(Torneio, ListandoTorneio)
admin.site.register(HistoricoPartida, ListandoHistoricoPartida)
admin.site.register(Mesa, ListandoMesa)
admin.site.register(Codigo_Mesa, ListandoCodigoMesa)
admin.site.register(ResultadoTorneio)