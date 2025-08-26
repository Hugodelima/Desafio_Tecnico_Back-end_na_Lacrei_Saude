from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Profissional
from .serializers import ProfissionalSerializer
from django.db.models import Q
from consultas.serializers import ConsultaSerializer  # Corrige a importação

class ProfissionalViewSet(viewsets.ModelViewSet):
    serializer_class = ProfissionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profissional.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['profissao']
    ordering_fields = ['nome_social', 'profissao', 'created_at']
    ordering = ['nome_social']
    search_fields = ['nome_social', 'profissao', 'endereco', 'contato']

    def get_queryset(self):
        queryset = Profissional.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_social__icontains=search) | 
                Q(profissao__icontains=search) |
                Q(endereco__icontains=search) |
                Q(contato__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return Response({"message": "Endpoint para informações do profissional autenticado"})

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def consultas(self, request, pk=None):
        """Endpoint para listar consultas de um profissional específico"""
        profissional = self.get_object()
        consultas = profissional.consultas.all()
        
        # Aplicar filtros nas consultas do profissional
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        
        if data_inicio:
            try:
                from datetime import datetime
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                consultas = consultas.filter(data__date__gte=data_inicio_dt)
            except ValueError:
                pass
        
        if data_fim:
            try:
                from datetime import datetime
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
                consultas = consultas.filter(data__date__lte=data_fim_dt)
            except ValueError:
                pass
        
        # Use a importação correta
        serializer = ConsultaSerializer(consultas, many=True)
        return Response(serializer.data)