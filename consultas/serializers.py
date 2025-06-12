from rest_framework import serializers
from .models import Consulta
from django.utils.timezone import now

class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'

    def validate_data(self, value):
        if value < now():
            raise serializers.ValidationError("A data da consulta deve ser futura.")
        return value
