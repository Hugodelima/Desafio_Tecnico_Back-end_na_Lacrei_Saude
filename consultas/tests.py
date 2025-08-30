from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from profissionais.models import Profissional
from .models import Consulta
from django.utils.translation import gettext_lazy as _

class ConsultaCRUDTests(APITestCase):
    """Testes de CRUD completo para consultas"""
    
    def setUp(self):
        # Criar usuários
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            email='test2@example.com'
        )
        
        # Criar profissionais
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
        
        # Criar consultas
        self.consulta = Consulta.objects.create(
            data=timezone.now() + timedelta(days=1),
            profissional=self.profissional1
        )
        
        # URLs
        self.list_url = reverse('consulta-list')
        self.detail_url = reverse('consulta-detail', args=[self.consulta.id])
        
        # Autenticar primeiro usuário
        self.client = APIClient()
        
        # DEBUG CI
        print("=== DEBUG CI ===")
        print(f"Testing URL: /api/auth/token/")
        
        token_response = self.client.post('/api/auth/token/', {
            'username': 'testuser', 
            'password': 'testpass123'
        }, format='json')
        
        # Se for redirecionamento, seguir o redirect
        if hasattr(token_response, 'status_code') and token_response.status_code in [301, 302]:
            print(f"Redirect detected! Following to: {token_response.url}")
            token_response = self.client.post(token_response.url, {
                'username': 'testuser', 
                'password': 'testpass123'
            }, format='json')
        
        print(f"Final response type: {type(token_response)}")
        print(f"Final response status: {getattr(token_response, 'status_code', 'No status')}")
        
        if hasattr(token_response, 'data'):
            print("✅ Response HAS data attribute")
            print(f"Response data keys: {list(token_response.data.keys())}")
            self.token = token_response.data['access']
            print("✅ Token obtained successfully")
        else:
            print("❌ Response still has NO data attribute after redirect")
            print(f"Available attributes: {[attr for attr in dir(token_response) if not attr.startswith('_')]}")
            if hasattr(token_response, 'content'):
                print(f"Response content: {token_response.content}")
            self.fail("Authentication failed even after following redirect")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_listar_consultas_autenticado(self):
        """Testa listagem de consultas con autenticação"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_listar_consultas_nao_autenticado(self):
        """Testa que usuário não autenticado não pode listar consultas"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('message', response.data)

    def test_criar_consulta_autenticado(self):
        """Testa criação de consulta con autenticação"""
        data = {
            'data': (timezone.now() + timedelta(days=2)).isoformat(),
            'profissional': self.profissional2.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_criar_consulta_nao_autenticado(self):
        """Testa que usuário não autenticado não pode criar consultas"""
        client_nao_autenticado = APIClient()
        data = {
            'data': (timezone.now() + timedelta(days=2)).isoformat(),
            'profissional': self.profissional1.id
        }
        response = client_nao_autenticado.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_obter_consulta_por_id_autenticado(self):
        """Testa visualização de consulta específica con autenticação"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profissional'], self.profissional1.id)

    def test_obter_consulta_por_id_nao_autenticado(self):
        """Testa que usuário não autenticado não pode visualizar consulta específica"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_atualizar_consulta_autenticado(self):
        """Testa atualização de consulta con autenticação"""
        nova_data = (timezone.now() + timedelta(days=3)).isoformat()
        data = {
            'data': nova_data,
            'profissional': self.profissional1.id
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.data.isoformat(), nova_data)

    def test_atualizar_consulta_nao_autenticado(self):
        """Testa que usuário não autenticado não pode atualizar consultas"""
        client_nao_autenticado = APIClient()
        data = {
            'data': (timezone.now() + timedelta(days=3)).isoformat(),
            'profissional': self.profissional1.id
        }
        response = client_nao_autenticado.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_deletar_consulta_autenticado(self):
        """Testa exclusão de consulta con autenticação"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Consulta.objects.count(), 0)

    def test_deletar_consulta_nao_autenticado(self):
        """Testa que usuário não autenticado não pode deletar consultas"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_criar_consulta_data_passada(self):
        """Testa que não é possível criar consulta con data passada"""
        data = {
            'data': (timezone.now() - timedelta(days=1)).isoformat(),
            'profissional': self.profissional1.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

    def test_criar_consulta_formato_data_invalido(self):
        """Testa validação de formato de data inválido"""
        data = {
            'data': 'data-invalida',
            'profissional': self.profissional1.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

class ConsultaConflitoTests(APITestCase):
    """Testes de conflitos de agendamento"""
    
    def setUp(self):
        # Criar usuário
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Criar profissional
        self.profissional = Profissional.objects.create(
            nome_social="Dr. Teste",
            profissao="Cardiologia",
            endereco="Rua Teste, 123",
            contato="teste@example.com"
        )
        
        # Criar consulta existente
        self.data_consulta = timezone.now() + timedelta(days=1)
        self.consulta_existente = Consulta.objects.create(
            data=self.data_consulta,
            profissional=self.profissional
        )
        
        # Autenticação
        self.client = APIClient()
        
