from rest_framework import viewsets
from .models import Profissional
from .serializers import ProfissionalSerializer
from django.db.models import Q

class ProfissionalViewSet(viewsets.ModelViewSet):
    serializer_class = ProfissionalSerializer
    queryset = Profissional.objects.all() 
    
    def get_queryset(self):
        queryset = Profissional.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_social__icontains=search) | 
                Q(profissao__icontains=search)
            )
        return queryset