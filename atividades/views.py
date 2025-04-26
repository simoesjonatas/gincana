from django.shortcuts import render
from .models import Crianca, Resultado
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce

def ranking_view(request):
    # Pontuação total por criança (mesmo sem registros)
    ranking_qs = Crianca.objects.annotate(
        total=Coalesce(Sum(
            ExpressionWrapper(
                F('resultado__quantidade') * F('resultado__atividade__pontos'),
                output_field=FloatField()
            )
        ), Value(0.0))
    ).order_by('-total', 'nome')  # desempate por nome

    # Calcular posições com empate
    ranking = []
    last_pontuacao = None
    posicao = 0
    empate = 0

    for i, item in enumerate(ranking_qs, start=1):
        if item.total != last_pontuacao:
            posicao = i
            last_pontuacao = item.total
        ranking.append({
            'posicao': posicao,
            'nome': item.nome.upper(),
            'total': item.total,
        })

    return render(request, 'ranking.html', {'ranking': ranking})
