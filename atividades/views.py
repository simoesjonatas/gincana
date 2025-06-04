from django.shortcuts import render
from .models import Crianca, Resultado
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce
from django.db.models import FloatField

def ranking_view(request):

    ranking_qs = Crianca.objects.annotate(
        total=Coalesce(Sum(
            ExpressionWrapper(
                F('resultado__quantidade') * F('resultado__atividade__pontos'),
                output_field=FloatField()
            )
        ), Value(0.0))
    ).order_by('-total', 'nome')

    # Descobrir os 3 maiores totais distintos
    totais_distintos = sorted(
        {item.total for item in ranking_qs if item.total > 0},
        reverse=True
    )[:3]

    ranking = []
    last_pontuacao = None
    posicao = 0

    for i, item in enumerate(ranking_qs, start=1):
        if item.total != last_pontuacao:
            posicao = i
            last_pontuacao = item.total

        if item.total == totais_distintos[0]:
            medalha = 'ouro'
        elif len(totais_distintos) > 1 and item.total == totais_distintos[1]:
            medalha = 'prata'
        elif len(totais_distintos) > 2 and item.total == totais_distintos[2]:
            medalha = 'bronze'
        else:
            medalha = None

        ranking.append({
            'posicao': posicao,
            'nome': item.nome.upper(),
            'total': item.total,
            'medalha': medalha,
        })

    return render(request, 'ranking.html', {'ranking': ranking})
