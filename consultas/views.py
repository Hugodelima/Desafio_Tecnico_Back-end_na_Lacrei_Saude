from rest_framework import viewsets, permissions, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from .models import Consulta
from .serializers import ConsultaSerializer

class ConsultaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de consultas médicas.
    """
    
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['profissional', 'data']
    ordering_fields = ['data', 'profissional__nome_social', 'created_at']
    ordering = ['-data']
    search_fields = ['profissional__nome_social', 'profissional__profissao']

    def handle_exception(self, exc):
        """
        Manipula exceções e retorna mensagens de erro consistentes
        """
        if isinstance(exc, serializers.ValidationError):
            return Response(
                {
                    'error': 'Dados inválidos',
                    'details': exc.detail,
                    'message': _('Verifique os campos informados e tente novamente.')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, permissions.exceptions.NotAuthenticated):
            return Response(
                {
                    'error': 'Não autenticado',
                    'message': _('As credenciais de autenticação não foram fornecidas.')
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif isinstance(exc, permissions.exceptions.PermissionDenied):
            return Response(
                {
                    'error': 'Permissão negada',
                    'message': _('Você não tem permissão para executar esta ação.')
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Log do erro para debugging
        print(f"Erro não tratado: {str(exc)}")
        
        return Response(
            {
                'error': 'Erro interno do servidor',
                'message': _('Ocorreu um erro inesperado. '
                           'Nossa equipe já foi notificada e está trabalhando na solução.')
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def get_queryset(self):
        """
        Retorna queryset de consultas com filtros aplicados.
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
                # Mensagem de erro melhorada para filtro inválido
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
        status_filter = self.request.query_params.get('status')
        if status_filter == 'futuras':
            queryset = queryset.filter(data__gte=timezone.now())
        elif status_filter == 'passadas':
            queryset = queryset.filter(data__lt=timezone.now())
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Sobrescreve o método list para retornar estrutura consistente
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return self.handle_exception(e)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def minhas_consultas(self, request):
        """
        Endpoint para listar consultas do usuário autenticado.
        """
        try:
            consultas = self.get_queryset()
            serializer = self.get_serializer(consultas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': 'Erro ao buscar consultas',
                'message': _('Não foi possível recuperar suas consultas. Tente novamente.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def resumo(self, request):
        """
        Endpoint de resumo estatístico das consultas.
        """
        try:
            total_consultas = Consulta.objects.count()
            consultas_futuras = Consulta.objects.filter(data__gte=timezone.now()).count()
            consultas_passadas = Consulta.objects.filter(data__lt=timezone.now()).count()
            
            return Response({
                'total_consultas': total_consultas,
                'consultas_futuras': consultas_futuras,
                'consultas_passadas': consultas_passadas,
                'message': _('Resumo estatístico gerado com sucesso.')
            })
        except Exception as e:
            return Response({
                'error': 'Erro ao gerar resumo',
                'message': _('Não foi possível gerar o resumo estatístico. Tente novamente.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)