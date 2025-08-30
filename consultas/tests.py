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
        token_response = self.client.post(
            '/api/auth/token/',  # CORRIGIDO: URL com barra
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )
        self.token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_listar_consultas_autenticado(self):
        """Testa listagem de consultas com autenticação"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # A estrutura agora retorna lista direta, não mais com 'results'
        self.assertEqual(len(response.data), 1)

    def test_listar_consultas_nao_autenticado(self):
        """Testa que usuário não autenticado não pode listar consultas"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.get(self.list_url)
        # Agora deve retornar 401 con mensagem estruturada
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('message', response.data)

    def test_criar_consulta_autenticado(self):
        """Testa criação de consulta com autenticação"""
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
        """Testa visualização de consulta específica com autenticação"""
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
        token_response = self.client.post(
            '/api/auth/token/',  # CORRIGIDO: URL com barra
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )
        self.token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.list_url = reverse('consulta-list')

    def test_criar_consulta_mesmo_horario_mesmo_profissional(self):
        """Testa conflito: mesma data/hora e mesmo profissional"""
        data = {
            'data': self.data_consulta.isoformat(),
            'profissional': self.profissional.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

    def test_criar_consulta_mesmo_horario_profissional_diferente(self):
        """Testa que é permitido mesmo horário com profissional diferente"""
        profissional2 = Profissional.objects.create(
            nome_social="Dra. Outra",
            profissao="Pediatria",
            endereco="Rua Outra, 456",
            contato="outra@example.com"
        )
        
        data = {
            'data': self.data_consulta.isoformat(),
            'profissional': profissional2.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_atualizar_consulta_mesmo_horario_mesma_consulta(self):
        """Testa que é permitido atualizar a mesma consulta para o mesmo horário"""
        data = {
            'data': self.data_consulta.isoformat(),
            'profissional': self.profissional.id
        }
        url = reverse('consulta-detail', args=[self.consulta_existente.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_atualizar_consulta_mesmo_horario_outra_consulta(self):
        """Testa conflito ao atualizar consulta para horário ocupado por outra consulta"""
        # Criar segunda consulta
        consulta2 = Consulta.objects.create(
            data=timezone.now() + timedelta(days=2),
            profissional=self.profissional
        )
        
        # Tentar atualizar segunda consulta para o horário da primeira
        data = {
            'data': self.data_consulta.isoformat(),
            'profissional': self.profissional.id
        }
        url = reverse('consulta-detail', args=[consulta2.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

class ConsultaAuthorizationTests(APITestCase):
    """Testes de autorização entre usuários diferentes"""
    
    def setUp(self):
        # Criar dois usuários
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        
        # Criar profissional
        self.profissional = Profissional.objects.create(
            nome_social="Dr. Teste",
            profissao="Cardiologia",
            endereco="Rua Teste, 123",
            contato="teste@example.com"
        )
        
        # Criar consulta com user1 autenticado
        self.client = APIClient()
        token_response = self.client.post(
            '/api/auth/token/',  # CORRIGIDO: URL com barra
            {'username': 'user1', 'password': 'pass123'},
            format='json'
        )
        self.token_user1 = token_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_user1}')
        
        # Criar consulta
        response = self.client.post(
            reverse('consulta-list'),
            {
                'data': (timezone.now() + timedelta(days=1)).isoformat(),
                'profissional': self.profissional.id
            },
            format='json'
        )
        self.consulta_id = response.data['id']
        self.detail_url = reverse('consulta-detail', args=[self.consulta_id])

    def test_usuario2_pode_acessar_consulta_usuario1(self):
        """Testa que usuário2 pode acessar consulta criada por usuário1"""
        # Autenticar como user2
        token_response = self.client.post(
            '/api/auth/token/',  # CORRIGIDO: URL com barra
            {'username': 'user2', 'password': 'pass123'},
            format='json'
        )
        token_user2 = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_user2}')
        
        # Tentar acessar consulta do user1
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_usuario2_pode_editar_consulta_usuario1(self):
        """Testa que usuário2 pode editar consulta criada por usuário1"""
        # Autenticar como user2
        token_response = self.client.post(
            '/api/auth/token/',  # CORRIGIDO: URL com barra
            {'username': 'user2', 'password': 'pass123'},
            format='json'
        )
        token_user2 = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_user2}')
        
        # Tentar editar consulta do user1
        data = {
            'data': (timezone.now() + timedelta(days=2)).isoformat(),
            'profissional': self.profissional.id
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_usuario2_pode_deletar_consulta_usuario1(self):
        """Testa que usuário2 pode deletar consulta criada por usuário1"""
        # Autenticar como user2
        token_response = self.client.post(
            '/api/auth/token/',  # CORRIGIDO: URL com barra
            {'username': 'user2', 'password': 'pass123'},
            format='json'
        )
        token_user2 = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_user2}')
        
        # Tentar deletar consulta do user1
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)