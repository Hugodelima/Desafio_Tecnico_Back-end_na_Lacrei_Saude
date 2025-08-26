from rest_framework import serializers
from .models import Consulta
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class ConsultaSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.CharField(source='profissional.nome_social', read_only=True)
    profissional_especialidade = serializers.CharField(source='profissional.profissao', read_only=True)
    
    class Meta:
        model = Consulta
        fields = [
            'id', 'data', 'profissional', 'profissional_nome', 
            'profissional_especialidade', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

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
            consultas_existentes = Consulta.objects.filter(
                profissional=profissional,
                data=data_consulta
            )
            
            if self.instance:
                consultas_existentes = consultas_existentes.exclude(pk=self.instance.pk)
            
            if consultas_existentes.exists():
                raise serializers.ValidationError(
                    f"Já existe uma consulta agendada para {profissional.nome_social} "
                    f"no horário {data_consulta.strftime('%d/%m/%Y %H:%M')}"
                )
        
        return data