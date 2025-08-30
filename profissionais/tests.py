from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profissional
from django.utils.translation import gettext_lazy as _

class ProfissionalCRUDTests(APITestCase):
    """Testes de CRUD completo para profissionais"""
    
    def setUp(self):
        # Criar usuários
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
        
        # Autenticação
        self.client = APIClient()
        
        # DEBUG CI - Adicione estas linhas
        print("=== DEBUG CI PROFISSIONAIS CRUD ===")
        print(f"Testing URL: /api/auth/token/")
        
        token_response = self.client.post('/api/auth/token/', {
            'username': 'testuser', 
            'password': 'testpass123'
        }, format='json')
        
        # DEBUG: Verificar a resposta
        print(f"Response type: {type(token_response)}")
        print(f"Response status: {getattr(token_response, 'status_code', 'No status')}")
        
        if hasattr(token_response, 'data'):
            print("✅ Response HAS data attribute")
            print(f"Response data keys: {list(token_response.data.keys())}")
            self.token = token_response.data['access']
            print("✅ Token obtained successfully")
        else:
            print("❌ Response has NO data attribute")
            print(f"Available attributes: {[attr for attr in dir(token_response) if not attr.startswith('_')]}")
            
            # Tentar fallback para conteúdo bruto
            if hasattr(token_response, 'content'):
                print(f"Response content: {token_response.content}")
            if hasattr(token_response, 'url'):
                print(f"Redirect URL: {token_response.url}")
                
            self.fail("Authentication failed - check JWT configuration")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # URLs
        self.list_url = reverse('profissional-list')
        self.detail_url = reverse('profissional-detail', args=[self.profissional.id])

    def test_listar_profissionais_autenticado(self):
        """Testa listagem de profissionais com autenticação"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_listar_profissionais_nao_autenticado(self):
        """Testa que usuário não autenticado não pode listar profissionais"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_criar_profissional_autenticado(self):
        """Testa criação de profissional com autenticação"""
        data = {
            'nome_social': 'Dra. Nova',
            'profissao': 'Pediatria',
            'endereco': 'Av. Nova, 456',
            'contato': 'nova@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissional.objects.count(), 2)

    def test_criar_profissional_nao_autenticado(self):
        """Testa que usuário não autenticado não pode criar profissionais"""
        client_nao_autenticado = APIClient()
        data = {
            'nome_social': 'Dra. Nova',
            'profissao': 'Pediatria',
            'endereco': 'Av. Nova, 456',
            'contato': 'nova@example.com'
        }
        response = client_nao_autenticado.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_obter_profissional_por_id_autenticado(self):
        """Testa visualização de profissional específico com autenticação"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome_social'], 'Dr. Teste')

    def test_obter_profissional_por_id_nao_autenticado(self):
        """Testa que usuário não autenticado não pode visualizar profissional específico"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_atualizar_profissional_autenticado(self):
        """Testa atualização de profissional com autenticação"""
        data = {'nome_social': 'Dr. Teste Atualizado'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.nome_social, 'Dr. Teste Atualizado')

    def test_atualizar_profissional_nao_autenticado(self):
        """Testa que usuário não autenticado não pode atualizar profissionais"""
        client_nao_autenticado = APIClient()
        data = {'nome_social': 'Dr. Teste Atualizado'}
        response = client_nao_autenticado.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_deletar_profissional_autenticado(self):
        """Testa exclusão de profissional com autenticação"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profissional.objects.count(), 0)

    def test_deletar_profissional_nao_autenticado(self):
        """Testa que usuário não autenticado não pode deletar profissionais"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

class ProfissionalValidationTests(APITestCase):
    """Testes de validação para profissionais"""
    
    def setUp(self):
        # Criar usuário
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Autenticação
        self.client = APIClient()
        
        # DEBUG CI - Adicione estas linhas
        print("=== DEBUG CI PROFISSIONAIS VALIDATION ===")
        print(f"Testing URL: /api/auth/token/")
        
        token_response = self.client.post('/api/auth/token/', {
            'username': 'testuser', 
            'password': 'testpass123'
        }, format='json')
        
        # DEBUG: Verificar a resposta
        print(f"Response type: {type(token_response)}")
        print(f"Response status: {getattr(token_response, 'status_code', 'No status')}")
        
        if hasattr(token_response, 'data'):
            print("✅ Response HAS data attribute")
            self.token = token_response.data['access']
            print("✅ Token obtained successfully")
        else:
            print("❌ Response has NO data attribute")
            print(f"Available attributes: {[attr for attr in dir(token_response) if not attr.startswith('_')]}")
            self.fail("Authentication failed")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.list_url = reverse('profissional-list')

    def test_criar_profissional_sem_nome(self):
        """Testa que não é possível criar profissional sem nome"""
        data = {
            'profissao': 'Cardiologia',
            'endereco': 'Rua Teste, 123',
            'contato': 'teste@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

    def test_criar_profissional_sem_profissao(self):
        """Testa que não é possível criar profissional sem profissão"""
        data = {
            'nome_social': 'Dr. Teste',
            'endereco': 'Rua Teste, 123',
            'contato': 'teste@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

    def test_criar_profissional_campos_vazios(self):
        """Testa validação de campos vazios"""
        data = {
            'nome_social': '',
            'profissao': '',
            'endereco': 'Rua Teste, 123',
            'contato': 'teste@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

    def test_criar_profissional_nome_curto(self):
        """Testa validação de nome muito curto"""
        data = {
            'nome_social': 'A',
            'profissao': 'Cardiologia',
            'endereco': 'Rua Teste, 123',
            'contato': 'teste@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

    def test_criar_profissional_profissao_curta(self):
        """Testa validação de profissão muito curta"""
        data = {
            'nome_social': 'Dr. Teste',
            'profissao': 'Ca',
            'endereco': 'Rua Teste, 123',
            'contato': 'teste@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)

    def test_criar_profissional_contato_invalido(self):
        """Testa validação de contato inválido"""
        data = {
            'nome_social': 'Dr. Teste',
            'profissao': 'Cardiologia',
            'endereco': 'Rua Teste, 123',
            'contato': 'invalido'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)