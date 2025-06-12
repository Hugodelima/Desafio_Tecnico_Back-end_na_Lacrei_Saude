from django.db import models

class Profissional(models.Model):
    nome_social = models.CharField(max_length=100)
    profissao = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    contato = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_social
