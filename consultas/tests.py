from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from profissionais.models import Profissional
from .models import Consulta

class ConsultaTests(APITestCase):
    def setUp(self):
        self.profissional = Profissional.objects.create(
            nome_social="Dra. Carla",
            profissao="Ginecologista",
            endereco="Av. Central, 99",
            contato="carla@exemplo.com"
        )
        self.url = "/api/consultas/"
        self.data = {
            "data": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            "profissional": self.profissional.id
        }
        self.consulta = Consulta.objects.create(
            data=self.data["data"],
            profissional=self.profissional
        )

    def test_criar_consulta(self):
        new_data = self.data.copy()
        new_data["data"] = (timezone.now() + timezone.timedelta(days=2)).isoformat()
        response = self.client.post(self.url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_listar_consultas(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_obter_consulta_por_id(self):
        response = self.client.get(f"{self.url}{self.consulta.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profissional"], self.profissional.id)

    def test_atualizar_consulta(self):
        nova_data = (timezone.now() + timezone.timedelta(days=3)).isoformat()
        updated_data = {
            "data": nova_data,
            "profissional": self.profissional.id
        }
        response = self.client.put(f"{self.url}{self.consulta.id}/", updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.data.isoformat(), nova_data)

    def test_deletar_consulta(self):
        response = self.client.delete(f"{self.url}{self.consulta.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Consulta.objects.count(), 0)
