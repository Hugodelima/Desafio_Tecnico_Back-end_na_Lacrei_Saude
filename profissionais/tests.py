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
        
        # DEBUG CI
        print("=== DEBUG CI ===")
        print(f"Testing URL: /api/auth/token/")
        
        # SOLUÇÃO: Remover follow=True e usar abordagem diferente
        token_response = self.client.post('/api/auth/token/', {
            'username': 'testuser', 
            'password': 'testpass123'
        }, format='json')
        
        print(f"Response type: {type(token_response)}")
        print(f"Response status: {getattr(token_response, 'status_code', 'No status')}")
        
        if hasattr(token_response, 'data'):
            print("✅ Response HAS data attribute")
            print(f"Response data keys: {list(token_response.data.keys())}")
            
            # Verificar se é um erro 405
            if token_response.status_code == 405:
                print(f"Error detail: {token_response.data.get('detail', 'No detail')}")
                # TENTATIVA ALTERNATIVA: Usar GET em vez de POST (apenas para teste)
                print("Trying GET request instead of POST...")
                token_response = self.client.get('/api/auth/token/', format='json')
                print(f"GET response status: {token_response.status_code}")
                print(f"GET response data: {getattr(token_response, 'data', 'No data')}")
                self.fail("Authentication failed - method not allowed")
            
            # Verificar se temos o token de acesso
            elif 'access' in token_response.data:
                self.token = token_response.data['access']
                print("✅ Token obtained successfully")
            else:
                print("❌ Response has data but no access token")
                print(f"Full response data: {token_response.data}")
                self.fail("Authentication failed - no access token in response")
        else:
            print("❌ Response has NO data attribute")
            print(f"Available attributes: {[attr for attr in dir(token_response) if not attr.startswith('_')]}")
            
            # Se for redirecionamento, tentar a URL completa
            if hasattr(token_response, 'url') and token_response.status_code in [301, 302]:
                print(f"Redirect detected to: {token_response.url}")
                print("Trying with full URL...")
                token_response = self.client.post(token_response.url, {
                    'username': 'testuser', 
                    'password': 'testpass123'
                }, format='json')
                
                if hasattr(token_response, 'data') and 'access' in token_response.data:
                    self.token = token_response.data['access']
                else:
                    self.fail("Authentication failed after redirect")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
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
        
