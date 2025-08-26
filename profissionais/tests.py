from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profissional

class ProfissionalAuthTests(APITestCase):
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Criar profissional para testes
        self.profissional = Profissional.objects.create(
            nome_social="Dr. Teste",
            profissao="Cardiologista",
            endereco="Rua Teste, 123",
            contato="teste@example.com"
        )
        
        # URLs
        self.list_url = reverse('profissional-list')
        self.detail_url = reverse('profissional-detail', args=[self.profissional.id])
        
        # Obter token JWT
        self.client = APIClient()
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'testuser', 'password': 'testpass123'},
            format='json'
        )
        self.token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_list_profissionais_autenticado(self):
        """Testa listagem de profissionais com autenticação"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_profissionais_nao_autenticado(self):
        """Testa que usuário não autenticado não pode acessar"""
        client_nao_autenticado = APIClient()
        response = client_nao_autenticado.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_profissional_autenticado(self):
        """Testa criação de profissional com autenticação"""
        data = {
            'nome_social': 'Dra. Nova',
            'profissao': 'Pediatra',
            'endereco': 'Av. Nova, 456',
            'contato': 'nova@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissional.objects.count(), 2)

    def test_retrieve_profissional_autenticado(self):
        """Testa visualização de detalhes com autenticação"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome_social'], 'Dr. Teste')

    def test_update_profissional_autenticado(self):
        """Testa atualização de profissional com autenticação"""
        data = {'nome_social': 'Dr. Teste Atualizado'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.nome_social, 'Dr. Teste Atualizado')

    def test_delete_profissional_autenticado(self):
        """Testa exclusão de profissional com autenticação"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profissional.objects.count(), 0)

    def test_search_profissionais_autenticado(self):
        """Testa busca de profissionais com autenticação"""
        response = self.client.get(self.list_url, {'search': 'Cardio'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ProfissionalJWTTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tokenuser',
            password='tokenpass123'
        )
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_obter_token_jwt(self):
        """Testa obtenção de token JWT"""
        response = self.client.post(
            self.token_url,
            {'username': 'tokenuser', 'password': 'tokenpass123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obter_token_com_credenciais_invalidas(self):
        """Testa tentativa de obter token com credenciais inválidas"""
        response = self.client.post(
            self.token_url,
            {'username': 'invalid', 'password': 'invalid'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Testa refresh do token JWT"""
        # Primeiro obtém o token
        token_response = self.client.post(
            self.token_url,
            {'username': 'tokenuser', 'password': 'tokenpass123'},
            format='json'
        )
        refresh_token = token_response.data['refresh']
        
        # Faz refresh
        response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)