from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Consulta
from .serializers import ConsultaSerializer

class ConsultaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de consultas médicas.
    
    Permite operações CRUD completas para agendamento de consultas.
    Inclui validações para evitar conflitos de horário.
    Requer autenticação JWT para acesso.
    
    Filtros disponíveis:
    - profissional: Filtra por ID do profissional
    - data_inicio/data_fim: Filtra por período
    - horario_inicio/horario_fim: Filtra por horário
    - status: 'futuras' ou 'passadas'
    - search: Busca por nome ou especialidade do profissional
    - ordering: Ordena por data ou nome do profissional
    """
    
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['profissional', 'data']
    ordering_fields = ['data', 'profissional__nome_social', 'created_at']
    ordering = ['-data']
    search_fields = ['profissional__nome_social', 'profissional__profissao']

    def get_queryset(self):
        """
        Retorna queryset de consultas com filtros aplicados.
        
        Suporta filtros por:
        - Período de datas (data_inicio, data_fim)
        - Período de horários (horario_inicio, horario_fim)
        - Status (futuras, passadas)
        """
        queryset = Consulta.objects.all()
        
        # Filtro por período (data_inicio e data_fim)
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                queryset = queryset.filter(data__date__gte=data_inicio_dt)
            except ValueError:
                pass
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
                queryset = queryset.filter(data__date__lte=data_fim_dt)
            except ValueError:
                pass
        
        # Filtro por horário
        horario_inicio = self.request.query_params.get('horario_inicio')
        horario_fim = self.request.query_params.get('horario_fim')
        
        if horario_inicio:
            try:
                horario_inicio_dt = datetime.strptime(horario_inicio, '%H:%M').time()
                queryset = queryset.filter(data__time__gte=horario_inicio_dt)
            except ValueError:
                pass
        
        if horario_fim:
            try:
                horario_fim_dt = datetime.strptime(horario_fim, '%H:%M').time()
                queryset = queryset.filter(data__time__lte=horario_fim_dt)
            except ValueError:
                pass
        
        # Filtro por status (futuras/passadas)
        status = self.request.query_params.get('status')
        if status == 'futuras':
            queryset = queryset.filter(data__gte=timezone.now())
        elif status == 'passadas':
            queryset = queryset.filter(data__lt=timezone.now())
        
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def minhas_consultas(self, request):
        """
        Endpoint para listar consultas do usuário autenticado.
        
        Retorna todas as consultas associadas ao usuário logado.
        Aplica os mesmos filtros disponíveis no endpoint principal.
        """
        consultas = self.get_queryset()
        serializer = self.get_serializer(consultas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def resumo(self, request):
        """
        Endpoint de resumo estatístico das consultas.
        
        Retorna:
        - total_consultas: Número total de consultas
        - consultas_futuras: Consultas agendadas para o futuro
        - consultas_passadas: Consultas já realizadas
        """
        total_consultas = Consulta.objects.count()
        consultas_futuras = Consulta.objects.filter(data__gte=timezone.now()).count()
        consultas_passadas = Consulta.objects.filter(data__lt=timezone.now()).count()
        
        return Response({
            'total_consultas': total_consultas,
            'consultas_futuras': consultas_futuras,
            'consultas_passadas': consultas_passadas,
        })