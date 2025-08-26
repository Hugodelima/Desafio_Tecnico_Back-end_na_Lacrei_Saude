from rest_framework import serializers
from .models import Consulta
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'

    def validate_data(self, value):
        """
        Valida se a data é futura
        """
        if value < now():
            raise serializers.ValidationError("A data da consulta deve ser futura.")
        return value

    def validate(self, data):
        """
        Validação personalizada para conflitos de agendamento
        """
        profissional = data.get('profissional')
        data_consulta = data.get('data')
        
        if profissional and data_consulta:
            # Verifica se já existe uma consulta para o mesmo profissional no mesmo horário
            consultas_existentes = Consulta.objects.filter(
                profissional=profissional,
                data=data_consulta
            )
            
            # Se estiver atualizando uma consulta existente, exclui a própria consulta da verificação
            if self.instance:
                consultas_existentes = consultas_existentes.exclude(pk=self.instance.pk)
            
            if consultas_existentes.exists():
                raise serializers.ValidationError(
                    f"Já existe uma consulta agendada para {profissional.nome_social} "
                    f"no horário {data_consulta.strftime('%d/%m/%Y %H:%M')}"
                )
        
        return data