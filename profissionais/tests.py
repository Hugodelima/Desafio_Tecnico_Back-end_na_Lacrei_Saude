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
        
        # SOLUÇÃO: Usar Client com follow=True para lidar automaticamente com redirecionamentos
        token_response = self.client.post('/api/auth/token/', {
            'username': 'testuser', 
            'password': 'testpass123'
        }, format='json', follow=True)  # ← ADICIONE follow=True AQUI
        
        print(f"Final response type: {type(token_response)}")
        print(f"Final response status: {getattr(token_response, 'status_code', 'No status')}")
        
        if hasattr(token_response, 'data'):
            print("✅ Response HAS data attribute")
            print(f"Response data keys: {list(token_response.data.keys())}")
            self.token = token_response.data['access']
            print("✅ Token obtained successfully")
        else:
            print("❌ Response still has NO data attribute")
            print(f"Available attributes: {[attr for attr in dir(token_response) if not attr.startswith('_')]}")
            if hasattr(token_response, 'content'):
                print(f"Response content: {token_response.content}")
            
            # TENTATIVA ALTERNATIVA: Usar a URL completa do testserver
            print("Trying alternative approach with testserver URL...")
            token_response = self.client.post('https://testserver/api/auth/token/', {
                'username': 'testuser', 
                'password': 'testpass123'
            }, format='json')
            
            if hasattr(token_response, 'data'):
                print("✅ Alternative approach worked!")
                self.token = token_response.data['access']
            else:
                print("❌ Alternative approach also failed")
                self.fail("All authentication attempts failed")
        
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
        
