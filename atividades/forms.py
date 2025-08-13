from django import forms

class UploadPlanilhaForm(forms.Form):
    arquivo = forms.FileField(
        label="Planilha (.xls ou .xlsx)",
        help_text="Colunas: 1ªSemana, 2ªSemana, ..., TOTAL; primeira coluna = nome da criança"
    )
