from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from profissionais.models import Profissional
from .models import Consulta

class ConsultaFilterTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.profissional1 = Profissional.objects.create(
            nome_social="Dr. Cardiologista",
            profissao="Cardiologia",
            endereco="Rua A, 123",
            contato="cardio@example.com"
        )
        
        self.profissional2 = Profissional.objects.create(
            nome_social="Dra. Pediatra",
            profissao="Pediatria",
            endereco="Rua B, 456",
            contato="pediatra@example.com"
        )
        
        # Criar consultas com datas específicas
        self.consulta1 = Consulta.objects.create(
            data=timezone.make_aware(datetime(2024, 1, 15, 10, 0)),
            profissional=self.profissional1
        )
        
        self.consulta2 = Consulta.objects.create(
            data=timezone.make_aware(datetime(2024, 1, 15, 14, 0)),
            profissional=self.profissional1
        )
        
        self.consulta3 = Consulta.objects.create(
            data=timezone.make_aware(datetime(2024, 1, 20, 9, 0)),
            profissional=self.profissional2
        )
        
        # Autenticação
        self.client = APIClient()
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )
        self.token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.list_url = reverse('consulta-list')

    def test_filter_by_profissional(self):
        """Testa filtro por profissional"""
        response = self.client.get(f'{self.list_url}?profissional={self.profissional1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve retornar 2 consultas do profissional1
        self.assertEqual(len(response.data), 2)

    def test_filter_by_data_range(self):
        """Testa filtro por período de datas"""
        response = self.client.get(f'{self.list_url}?data_inicio=2024-01-10&data_fim=2024-01-16')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve retornar 2 consultas entre 10 e 16 de janeiro
        self.assertEqual(len(response.data), 2)

    def test_ordering_by_data_asc(self):
        """Testa ordenação por data ascendente"""
        response = self.client.get(f'{self.list_url}?ordering=data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica se retornou resultados
        self.assertGreaterEqual(len(response.data), 2)

    def test_ordering_by_data_desc(self):
        """Testa ordenação por data descendente"""
        response = self.client.get(f'{self.list_url}?ordering=-data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica se retornou resultados
        self.assertGreaterEqual(len(response.data), 2)

    def test_search_by_profissional_nome(self):
        """Testa busca por nome do profissional"""
        response = self.client.get(f'{self.list_url}?search=Cardiologista')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deve retornar consultas do cardiologista
        self.assertEqual(len(response.data), 2)

    def test_resumo_endpoint(self):
        """Testa endpoint de resumo"""
        response = self.client.get(f'{self.list_url}resumo/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_consultas', response.data)