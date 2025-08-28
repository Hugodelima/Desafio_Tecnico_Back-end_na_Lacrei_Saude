from rest_framework import viewsets, permissions, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from .models import Profissional
from .serializers import ProfissionalSerializer
from django.db.models import Q
from consultas.serializers import ConsultaSerializer

class ProfissionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de profissionais de saúde.
    """
    
    serializer_class = ProfissionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profissional.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['profissao']
    ordering_fields = ['nome_social', 'profissao']
    ordering = ['nome_social']
    search_fields = ['nome_social', 'profissao', 'endereco', 'contato']

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
        
        return Response(
            {
                'error': 'Erro interno do servidor',
                'message': _('Ocorreu um erro inesperado. Tente novamente.')
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def get_queryset(self):
        """
        Retorna queryset de profissionais com filtros aplicados.
        """
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
    def me(self, request):
        """
        Endpoint para informações do profissional autenticado.
        """
        return Response({
            'message': _('Endpoint para informações do profissional autenticado.'),
            'info': _('Esta funcionalidade será implementada em breve.')
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def consultas(self, request, pk=None):
        """
        Lista consultas de um profissional específico.
        """
        try:
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
            
            serializer = ConsultaSerializer(consultas, many=True)
            return Response({
                'profissional': profissional.nome_social,
                'total_consultas': len(serializer.data),
                'consultas': serializer.data,
                'message': _('Consultas do profissional recuperadas com sucesso.')
            })
        except Exception as e:
            return Response({
                'error': 'Erro ao buscar consultas',
                'message': _('Não foi possível recuperar as consultas do profissional.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)