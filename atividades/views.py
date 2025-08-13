from django.shortcuts import render
from .models import Crianca, Resultado
from django.db.models import Sum, F, FloatField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce
from django.db.models import FloatField


from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .forms import UploadPlanilhaForm
from .import_planilha import importar_planilha

@require_http_methods(["GET", "POST"])
def upload_planilha_view(request):
    if request.method == "POST":
        form = UploadPlanilhaForm(request.POST, request.FILES)
        if form.is_valid():
            arq = form.cleaned_data["arquivo"]
            try:
                with transaction.atomic():
                    resumo = importar_planilha(arq)
                messages.success(
                    request,
                    f"Importação concluída: "
                    f"{resumo['criancas_criadas_ou_encontradas']} crianças, "
                    f"Semanas {', '.join(map(str, resumo['semanas_processadas']))}, "
                    f"{resumo['resultados_criados']} resultados."
                )
                # Redireciona para o ranking (ajuste o nome da url)
                return redirect(reverse("ranking"))
            except Exception as e:
                messages.error(request, f"Erro na importação: {e}")
    else:
        form = UploadPlanilhaForm()
    return render(request, "upload_planilha.html", {"form": form})



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
