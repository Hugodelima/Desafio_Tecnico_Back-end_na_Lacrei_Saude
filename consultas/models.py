from django.db import models
from profissionais.models import Profissional
from django.core.exceptions import ValidationError

class Consulta(models.Model):
    data = models.DateTimeField()
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name="consultas")
    created_at = models.DateTimeField(auto_now_add=True)  # Adicione este campo
    updated_at = models.DateTimeField(auto_now=True)      # Adicione este campo

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profissional', 'data'],
                name='unique_agendamento_profissional'
            )
        ]

    def clean(self):
        """
        Validação para impedir agendamentos conflitantes
        """
        if Consulta.objects.filter(
            profissional=self.profissional,
            data=self.data
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                f"Já existe uma consulta agendada para {self.profissional.nome_social} "
                f"no horário {self.data.strftime('%d/%m/%Y %H:%M')}"
            )

    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para executar a validação clean()
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consulta com {self.profissional.nome_social} em {self.data}"