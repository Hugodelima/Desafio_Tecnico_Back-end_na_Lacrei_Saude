from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Profissional

class ProfissionalSerializer(serializers.ModelSerializer):
    """
    Serializer para profissionais de saúde com mensagens de erro melhoradas
    """
    
    class Meta:
        model = Profissional
        fields = ['id', 'nome_social', 'profissao', 'endereco', 'contato']
        # Remova os campos created_at e updated_at se não existirem no modelo

    def validate_nome_social(self, value):
        """
        Validação do nome social
        """
        if not value.strip():
            raise serializers.ValidationError(
                _("O nome social não pode estar vazio. Por favor, informe o nome do profissional.")
            )
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                _("O nome social deve ter pelo menos 2 caracteres.")
            )
        
        return value.strip()

    def validate_profissao(self, value):
        """
        Validação da profissão
        """
        if not value.strip():
            raise serializers.ValidationError(
                _("A profissão não pode estar vazia. Por favor, informe a especialidade do profissional.")
            )
        
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _("A profissão deve ter pelo menos 3 caracteres.")
            )
        
        return value.strip()

    def validate_contato(self, value):
        """
        Validação básica do contato
        """
        if value and len(value.strip()) > 0:
            if '@' not in value and not value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
                raise serializers.ValidationError(
                    _("Formato de contato inválido. "
                      "Informe um email válido ou número de telefone.")
                )
        return value.strip() if value else value

    def to_internal_value(self, data):
        """
        Melhora as mensagens de erro de parsing dos dados
        """
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as e:
            improved_errors = {}
            for field, errors in e.detail.items():
                improved_errors[field] = []
                for error in errors:
                    if 'This field is required' in str(error):
                        improved_errors[field].append(
                            _("Campo obrigatório: {field} é necessário para cadastrar o profissional.").format(field=field)
                        )
                    elif 'expected a number but got' in str(error):
                        improved_errors[field].append(
                            _("Valor inválido: {field} deve ser um número.").format(field=field)
                        )
                    else:
                        improved_errors[field].append(str(error))
            
            raise serializers.ValidationError(improved_errors)

    def create(self, validated_data):
        """
        Criação com validações adicionais
        """
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({
                'non_field_errors': [
                    _("Erro ao criar profissional: {error}").format(error=str(e))
                ]
            })

    def update(self, instance, validated_data):
        """
        Atualização com validações adicionais
        """
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError({
                'non_field_errors': [
                    _("Erro ao atualizar profissional: {error}").format(error=str(e))
                ]
            })