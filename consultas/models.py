from django.db import models
from profissionais.models import Profissional

class Consulta(models.Model):
    data = models.DateTimeField()
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name="consultas")

    def __str__(self):
        return f"Consulta com {self.profissional.nome_social} em {self.data}"
