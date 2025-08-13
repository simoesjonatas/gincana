from django.urls import path
from .views import ranking_view, upload_planilha_view

urlpatterns = [
    path('ranking/', ranking_view, name='ranking'),
    path("importar/", upload_planilha_view, name="importar_planilha"),

]
