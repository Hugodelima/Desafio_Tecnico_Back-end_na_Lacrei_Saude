from rest_framework.test import APITestCase
from rest_framework import status
from .models import Profissional

class ProfissionalTests(APITestCase):
    def setUp(self):
        self.url = "/api/profissionais/"
        self.data = {
            "nome_social": "Dr. João Silva",
            "profissao": "Psicólogo",
            "endereco": "Rua das Rosas, 45",
            "contato": "joao@exemplo.com"
        }
        self.profissional = Profissional.objects.create(**self.data)

    def test_criar_profissional(self):
        data = self.data.copy()
        data["nome_social"] = "Dra. Maria"
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissional.objects.count(), 2)

    def test_listar_profissionais(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_obter_profissional_por_id(self):
        response = self.client.get(f"{self.url}{self.profissional.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome_social"], self.profissional.nome_social)

    def test_atualizar_profissional(self):
        updated_data = self.data.copy()
        updated_data["profissao"] = "Psicanalista"
        response = self.client.put(f"{self.url}{self.profissional.id}/", updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profissional.refresh_from_db()
        self.assertEqual(self.profissional.profissao, "Psicanalista")

    def test_deletar_profissional(self):
        response = self.client.delete(f"{self.url}{self.profissional.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profissional.objects.count(), 0)
