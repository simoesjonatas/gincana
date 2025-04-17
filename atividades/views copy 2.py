from django.shortcuts import render
from .models import Crianca, Resultado
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce

def ranking_view(request):
    # Pontuação total por criança, mesmo se ela não tiver registros
    ranking = Crianca.objects.annotate(
        total=Coalesce(Sum(
            ExpressionWrapper(
                F('resultado__quantidade') * F('resultado__atividade__pontos'),
                output_field=FloatField()
            )
        ), Value(0.0))
    ).order_by('-total')

    return render(request, 'ranking.html', {'ranking': ranking})
