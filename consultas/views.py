from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Consulta
from .serializers import ConsultaSerializer

class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()  # Mantenha esta linha
    serializer_class = ConsultaSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def minhas_consultas(self, request):
        consultas = Consulta.objects.all()
        serializer = self.get_serializer(consultas, many=True)
        return Response(serializer.data)