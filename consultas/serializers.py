from rest_framework import serializers
from .models import Consulta
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
        Valida se a data da consulta é futura
        """
        if value < now():
            raise serializers.ValidationError(
                _("Não é possível agendar consultas retroativas. "
                  "Por favor, selecione uma data e horário futuros.")
            )
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
                consulta_existente = consultas_existentes.first()
                raise serializers.ValidationError({
                    'data': [
                        _("Conflito de agendamento: Já existe uma consulta agendada para o Dr. {nome} "
                          "no dia {data} às {hora}. Por favor, escolha outro horário.").format(
                            nome=profissional.nome_social,
                            data=data_consulta.strftime('%d/%m/%Y'),
                            hora=data_consulta.strftime('%H:%M')
                        )
                    ]
                })
        
        return data

    def to_internal_value(self, data):
        """
        Melhora as mensagens de erro de parsing dos dados
        """
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as e:
            # Traduz e melhora mensagens de erro comuns
            improved_errors = {}
            for field, errors in e.detail.items():
                improved_errors[field] = []
                for error in errors:
                    if 'This field is required' in str(error):
                        improved_errors[field].append(
                            _("Campo obrigatório: {field} é necessário.").format(field=field)
                        )
                    elif 'Invalid datetime format' in str(error):
                        improved_errors[field].append(
                            _("Formato de data/hora inválido. "
                              "Use o formato: YYYY-MM-DDTHH:MM:SS (ex: 2024-01-15T14:30:00)")
                        )
                    else:
                        improved_errors[field].append(str(error))
            
            raise serializers.ValidationError(improved_errors)