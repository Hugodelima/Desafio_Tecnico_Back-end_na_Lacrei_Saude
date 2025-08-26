from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from profissionais.models import Profissional
from .models import Consulta

class ConsultaAuthTests(APITestCase):
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Criar profissional
        self.profissional = Profissional.objects.create(
            nome_social="Dr. Teste",
            profissao="Cardiologista",
            endereco="Rua Teste, 123",
            contato="teste@example.com"
        )
        
        # Criar consulta
        self.consulta = Consulta.objects.create(
            data=timezone.now() + timezone.timedelta(days=1),
            profissional=self.profissional
        )
        
        # URLs
        self.list_url = reverse('consulta-list')
        self.detail_url = reverse('consulta-detail', args=[self.consulta.id])
        
        # Obter token JWT
        self.client = APIClient()
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )
        self.token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_list_consultas_autenticado(self):
        """Testa listagem de consultas com autenticação"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_consultas_nao_autenticado(self):
        """Testa que usuário não autenticado não pode acessar consultas"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_consulta_autenticado(self):
        """Testa criação de consulta com autenticação"""
        data = {
            'data': (timezone.now() + timezone.timedelta(days=2)).isoformat(),
            'profissional': self.profissional.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_create_consulta_conflito_autenticado(self):
        """Testa validação de conflito com autenticação"""
        # Tenta criar consulta no mesmo horário
        data = {
            'data': self.consulta.data.isoformat(),
            'profissional': self.profissional.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Já existe uma consulta agendada', str(response.data))

    def test_retrieve_consulta_autenticado(self):
        """Testa visualização de consulta com autenticação"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profissional'], self.profissional.id)

    def test_update_consulta_autenticado(self):
        """Testa atualização de consulta com autenticação"""
        nova_data = (timezone.now() + timezone.timedelta(days=3)).isoformat()
        data = {'data': nova_data}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consulta.refresh_from_db()

    def test_delete_consulta_autenticado(self):
        """Testa exclusão de consulta com autenticação"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Consulta.objects.count(), 0)

    def test_minhas_consultas_endpoint(self):
        """Testa endpoint personalizado de minhas consultas"""
        response = self.client.get(f'{self.list_url}minhas_consultas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ConsultaValidationTests(APITestCase):
    def setUp(self):
        # Configuração para testes de validação
        self.user = User.objects.create_user(
            username='validationuser',
            password='validationpass123'
        )
        
        self.profissional = Profissional.objects.create(
            nome_social="Dr. Validation",
            profissao="Neurologista",
            endereco="Rua Validation, 456",
            contato="validation@example.com"
        )
        
        # Autenticação
        self.client = APIClient()
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'validationuser', 'password': 'validationpass123'},
            format='json'
        )
        self.token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.list_url = reverse('consulta-list')

    def test_create_consulta_data_passada(self):
        """Testa validação de data passada com autenticação"""
        data = {
            'data': (timezone.now() - timezone.timedelta(days=1)).isoformat(),
            'profissional': self.profissional.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('A data da consulta deve ser futura', str(response.data))