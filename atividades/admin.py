from django.contrib import admin
from .models import Crianca, Semana, Atividade, Resultado

class ResultadoInline(admin.TabularInline):  # ou admin.StackedInline
    model = Resultado
    extra = 1
    autocomplete_fields = ['semana', 'atividade']
    fields = ['semana', 'atividade', 'quantidade']
    show_change_link = True
    
class ResultadoInlinePorAtividade(admin.TabularInline):
    model = Resultado
    extra = 1
    autocomplete_fields = ['crianca', 'semana']
    fields = ['crianca', 'semana', 'quantidade']
    show_change_link = True


@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'turma']
    search_fields = ['nome', 'turma']
    ordering = ['nome']
    inlines = [ResultadoInline]  # <-- aqui está a mágica

@admin.register(Semana)
class SemanaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'data_inicio', 'data_fim']
    list_filter = ['data_inicio']
    ordering = ['numero']
    search_fields = ['numero', 'data_inicio']


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pontos']
    search_fields = ['nome']
    ordering = ['nome']
    inlines = [ResultadoInlinePorAtividade]


@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ['crianca', 'atividade', 'semana', 'quantidade', 'pontos_totais']
    list_filter = ['atividade', 'semana']
    search_fields = ['crianca__nome', 'atividade__nome']
    ordering = ['-semana__numero']

    def pontos_totais(self, obj):
        return obj.quantidade * obj.atividade.pontos

    pontos_totais.short_description = 'Pontos'
