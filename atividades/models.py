from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Crianca(models.Model):
    nome = models.CharField(max_length=100)
    turma = models.CharField(max_length=50, blank=True)
    idade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(12)],
        help_text="Idade da criança em anos (0–12)."
    )

    def __str__(self):
        return self.nome

class Semana(models.Model):
    numero = models.IntegerField()
    data_inicio = models.DateField()
    data_fim = models.DateField()

    def __str__(self):
        return f"Semana {self.numero} ({self.data_inicio} a {self.data_fim})"

class Atividade(models.Model):
    nome = models.CharField(max_length=100)
    pontos = models.FloatField()

    def __str__(self):
        return f"{self.nome} ({self.pontos} pts)"

class Resultado(models.Model):
    crianca = models.ForeignKey(Crianca, on_delete=models.CASCADE)
    semana = models.ForeignKey(Semana, on_delete=models.CASCADE)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def pontos_totais(self):
        return self.quantidade * self.atividade.pontos

    def __str__(self):
        return f"{self.crianca} - {self.atividade} x{self.quantidade} (Semana {self.semana.numero})"
