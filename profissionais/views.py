from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Profissional
from .serializers import ProfissionalSerializer
from django.db.models import Q

class ProfissionalViewSet(viewsets.ModelViewSet):
    serializer_class = ProfissionalSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profissional.objects.all()  # Adicione esta linha
    
    def get_queryset(self):
        queryset = Profissional.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_social__icontains=search) | 
                Q(profissao__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        return Response({"message": "Endpoint para informações do profissional autenticado"})