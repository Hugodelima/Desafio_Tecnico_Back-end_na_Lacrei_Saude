from rest_framework import serializers
from .models import Profissional

class ProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissional
        fields = '__all__'

    def validate_nome_social(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("O nome social deve ter ao menos 3 caracteres.")
        return value

    def validate_contato(self, value):
        value = value.strip()
        if "@" not in value and not value.isdigit():
            raise serializers.ValidationError("Contato deve ser e-mail ou número de telefone válido.")
        return value

    def validate_profissao(self, value):
        return value.strip().title() 

    def validate_endereco(self, value):
        return value.strip()
