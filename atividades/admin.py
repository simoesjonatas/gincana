from django.contrib import admin
from .models import Crianca, Semana, Atividade, Resultado

@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'turma']
    search_fields = ['nome', 'turma']
    ordering = ['nome']

@admin.register(Semana)
class SemanaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'data_inicio', 'data_fim']
    list_filter = ['data_inicio']
    ordering = ['numero']

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pontos']
    search_fields = ['nome']
    ordering = ['nome']

@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ['crianca', 'atividade', 'semana', 'quantidade', 'pontos_totais']
    list_filter = ['atividade', 'semana']
    search_fields = ['crianca__nome', 'atividade__nome']
    ordering = ['-semana__numero']

    def pontos_totais(self, obj):
        return obj.quantidade * obj.atividade.pontos

    pontos_totais.short_description = 'Pontos'
