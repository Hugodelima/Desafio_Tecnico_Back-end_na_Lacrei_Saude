from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profissional

class ProfissionalFilterTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Criar profissionais em ordem específica para testes de ordenação
        self.profissional2 = Profissional.objects.create(
            nome_social="Dr. Cardiologista Silva",
            profissao="Cardiologia",
            endereco="Rua do Coração, 123",
            contato="cardio.silva@example.com"
        )
        
        self.profissional1 = Profissional.objects.create(
            nome_social="Dra. Pediatra Santos",
            profissao="Pediatria",
            endereco="Avenida Criança, 456",
            contato="pediatra.santos@example.com"
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
        
        self.list_url = reverse('profissional-list')

    def test_filter_by_profissao(self):
        """Testa filtro por profissão"""
        response = self.client.get(f'{self.list_url}?profissao=Cardiologia')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_nome(self):
        """Testa busca por nome"""
        response = self.client.get(f'{self.list_url}?search=Cardiologista')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_ordering_by_nome_asc(self):
        """Testa ordenação por nome ascendente"""
        response = self.client.get(f'{self.list_url}?ordering=nome_social')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica se retornou resultados
        self.assertEqual(len(response.data), 2)

    def test_ordering_by_nome_desc(self):
        """Testa ordenação por nome descendente"""
        response = self.client.get(f'{self.list_url}?ordering=-nome_social')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica se retornou resultados
        self.assertEqual(len(response.data), 2)