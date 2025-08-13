# services/import_planilha.py

import io
import re
import math
import pandas as pd
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone

from .models import Crianca, Semana, Atividade, Resultado  # ajuste conforme sua app

# Aceita "1ªSemana", "1ª Semana", "2a Semana", "3A Semana", etc.
SEMANA_COL_RE = re.compile(r"^\s*(\d+)\s*[ªaA]?\s*Semana\s*$", re.IGNORECASE)


def _parse_decimal_br(value):
    """
    Aceita 10, 1,5, '6', 6.0, '', None, NaN, '-'.
    Retorna Decimal ou None (quando não for número).
    """
    if value is None:
        return None

    # pandas pode mandar float('nan')
    if isinstance(value, float) and math.isnan(value):
        return None

    # Se já é número (int/float/Decimal)
    if isinstance(value, (int, float, Decimal)):
        try:
            # Troca vírgula por ponto caso venha como string numérica
            return Decimal(str(value).replace(',', '.'))
        except (InvalidOperation, ValueError):
            return None

    s = str(value).strip()
    if not s or s.lower() in {"nan", "none", "-"}:
        return None

    s = s.replace(',', '.')
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def _descobrir_colunas_semana(df: pd.DataFrame):
    """
    Encontra colunas do tipo '1ªSemana', '1ª Semana', '2ªSemana', ... e retorna
    lista de tuplas (numero_semana:int, nome_coluna:str) na ordem em que aparecem.
    Ignora 'TOTAL'.
    """
    semanas = []
    # assumindo 1a coluna = nome
    for col in df.columns[1:]:
        if str(col).strip().upper() == "TOTAL":
            continue
        m = SEMANA_COL_RE.match(str(col))
        if m:
            numero = int(m.group(1))
            semanas.append((numero, col))
    return semanas


def _get_or_create_semana(numero: int):
    """
    Garante a Semana pelo número.
    Caso não exista, cria com datas = hoje (ajuste se preferir).
    """
    hoje = timezone.localdate()
    semana, _ = Semana.objects.get_or_create(
        numero=numero,
        defaults={"data_inicio": hoje, "data_fim": hoje},
    )
    return semana


def _get_or_create_atividade_por_nota(nota: Decimal):
    """
    Atividade cuja pontuação é a nota da célula, com quantidade=1 no Resultado.
    Isso mantém o ranking: soma(quantidade * pontos) == soma das notas por linha.
    Blindado para NUNCA criar atividade sem 'pontos'.
    """
    # Normaliza a nota para evitar ruídos tipo 1.500000
    try:
        nota_fmt = float(nota)
    except Exception:
        raise ValueError(f"Nota inválida: {nota!r}")

    nome_fmt = f"Nota {nota.normalize()}" if isinstance(nota, Decimal) else f"Nota {nota_fmt}"

    # IMPORTANTE: filtra por 'pontos' e também informa 'pontos' nos defaults.
    atividade, created = Atividade.objects.get_or_create(
        pontos=nota_fmt,
        defaults={"nome": nome_fmt, "pontos": nota_fmt},
    )

    # Opcional: caso tenha vindo sem nome por algum motivo, completa
    if not atividade.nome:
        atividade.nome = nome_fmt
        atividade.save(update_fields=["nome"])

    return atividade


@transaction.atomic
def importar_planilha(file_obj):
    """
    Lê XLS/XLSX no formato:
      - Primeira coluna: nome da criança (sem título ou qualquer título -> renomeada para 'NOME')
      - Demais colunas: '1ªSemana', '1ª Semana', '2ªSemana', ..., 'TOTAL' (ignorada)
      - Células podem ter decimal com vírgula. Vazias/NaN/ '-' são ignoradas.

    Estratégia:
      - Coleta as semanas presentes.
      - Para evitar duplicidade em reimportações, APAGA os Resultados existentes
        apenas para as (crianças x semanas) presentes na planilha e recria.
    """
    # Lê com pandas sem gravar em disco
    data = file_obj.read()
    bio = io.BytesIO(data)

    try:
        # engine é autodetectado; requer openpyxl para .xlsx e xlrd para .xls
        df = pd.read_excel(bio, header=0)
    except Exception as e:
        raise ValueError(f"Não foi possível ler a planilha: {e}")

    if df.shape[1] < 2:
        raise ValueError("Planilha deve ter ao menos 2 colunas (Nome e semanas).")

    # Normaliza nome da 1ª coluna (nome da criança), mesmo se vier Unnamed: 0
    df.rename(columns={df.columns[0]: "NOME"}, inplace=True)

    semanas_cols = _descobrir_colunas_semana(df)
    if not semanas_cols:
        raise ValueError("Não encontrei colunas de semana (ex.: '1ªSemana', '1ª Semana', '2ªSemana', ...).")

    # Lista de nomes (tratando NaN -> "")
    nomes = (
        df["NOME"]
        .astype(str)
        .map(lambda s: s.strip())
        .replace({"nan": ""})
    )

    # Mapeia/cria crianças
    nome_to_crianca = {}
    for nome in nomes:
        if not nome:
            continue
        crianca, _ = Crianca.objects.get_or_create(nome=nome)
        nome_to_crianca[nome] = crianca

    # Garante semanas
    numero_to_semana = {}
    for numero, _col in semanas_cols:
        numero_to_semana[numero] = _get_or_create_semana(numero)

    # Limpa resultados antigos para (crianças do arquivo) x (semanas do arquivo)
    criancas_ids = [c.id for c in nome_to_crianca.values()]
    semanas_ids = [s.id for s in numero_to_semana.values()]
    if criancas_ids and semanas_ids:
        Resultado.objects.filter(
            crianca_id__in=criancas_ids,
            semana_id__in=semanas_ids
        ).delete()

    # Recria resultados
    novos_resultados = []
    for _, row in df.iterrows():
        nome = str(row["NOME"]).strip()
        if not nome:
            continue
        crianca = nome_to_crianca.get(nome)
        if not crianca:
            continue

        for numero, col in semanas_cols:
            valor = _parse_decimal_br(row.get(col))
            if valor is None:
                continue
            if valor == 0:
                continue

            semana = numero_to_semana[numero]
            atividade = _get_or_create_atividade_por_nota(valor)

            novos_resultados.append(
                Resultado(
                    crianca=crianca,
                    semana=semana,
                    atividade=atividade,
                    quantidade=1,
                )
            )

    if novos_resultados:
        Resultado.objects.bulk_create(novos_resultados, ignore_conflicts=False)

    return {
        "criancas_criadas_ou_encontradas": len(nome_to_crianca),
        "semanas_processadas": [n for n, _ in semanas_cols],
        "resultados_criados": len(novos_resultados),
    }
