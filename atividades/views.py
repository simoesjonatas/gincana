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



def ranking_escolha(request):
    """
    Renderiza a tela com os dois botões:
    - Até 4 anos
    - 5 anos ou mais
    """
    return render(request, "ranking_escolha.html")


def _build_ranking(qs):
    """
    Monta a lista de ranking (posicao, nome, total, medalha) a partir de um QS de Crianca.
    """
    qs = qs.annotate(
        total=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("resultado__quantidade") * F("resultado__atividade__pontos"),
                    output_field=FloatField()
                )
            ),
            Value(0.0)
        )
    ).order_by("-total", "nome")

    # Top 3 totais distintos (> 0) para medalhas
    tops = sorted({c.total for c in qs if c.total and c.total > 0}, reverse=True)[:3]

    def medal_for(total):
        if not tops:
            return None
        if len(tops) > 0 and total == tops[0]:
            return "ouro"
        if len(tops) > 1 and total == tops[1]:
            return "prata"
        if len(tops) > 2 and total == tops[2]:
            return "bronze"
        return None

    ranking, last_total, posicao = [], None, 0
    for i, c in enumerate(qs, start=1):
        if c.total != last_total:
            posicao = i
            last_total = c.total
        ranking.append({
            "posicao": posicao,
            "nome": c.nome,          # o template já usa |upper quando renderiza
            "total": c.total,
            "medalha": medal_for(c.total),
        })
    return ranking


def ranking_por_faixa_ate4(request):
    """
    Ranking apenas das crianças com idade até 4 anos (inclusive).
    """
    qs = Crianca.objects.filter(idade__lte=4)
    ranking = _build_ranking(qs)
    return render(request, "ranking.html", {"ranking": ranking, "faixa": "Até 4 anos"})


def ranking_por_faixa_5mais(request):
    """
    Ranking apenas das crianças com idade a partir de 5 anos (inclusive).
    """
    qs = Crianca.objects.filter(idade__gte=5)
    ranking = _build_ranking(qs)
    return render(request, "ranking.html", {"ranking": ranking, "faixa": "5 anos ou mais"})
