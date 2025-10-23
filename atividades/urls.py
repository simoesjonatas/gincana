from django.urls import path
from .views import ranking_view, upload_planilha_view, ranking_por_faixa_ate4, ranking_por_faixa_5mais

urlpatterns = [
    path('ranking/', ranking_view, name='ranking'),
    path("importar/", upload_planilha_view, name="importar_planilha"),
    path("ranking/ate-4/", ranking_por_faixa_ate4, name="ranking_ate4"),
    path("ranking/5-mais/",ranking_por_faixa_5mais, name="ranking_5mais"),

]
