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
        
        # Cria uma data base para os testes
        self.data_futura = timezone.now() + timezone.timedelta(days=1)
        self.data = {
            "data": self.data_futura.isoformat(),
            "profissional": self.profissional.id
        }
        
        # Cria uma consulta existente
        self.consulta = Consulta.objects.create(
            data=self.data_futura,
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

    def test_nao_deve_permitir_duas_consultas_mesmo_horario(self):
        """
        Teste para validar que não é possível agendar duas consultas
        para o mesmo profissional no mesmo horário
        """
        # Tenta criar outra consulta no mesmo horário
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Já existe uma consulta agendada", str(response.data))

    def test_deve_permitir_consultas_diferentes_horarios(self):
        """
        Teste para validar que é possível agendar consultas em horários diferentes
        para o mesmo profissional
        """
        new_data = self.data.copy()
        new_data["data"] = (self.data_futura + timezone.timedelta(hours=1)).isoformat()
        
        response = self.client.post(self.url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 2)

    def test_deve_permitir_atualizacao_mesma_consulta(self):
        """
        Teste para validar que é possível atualizar a mesma consulta
        sem conflito com ela mesma
        """
        updated_data = {
            "data": self.data_futura.isoformat(),  # Mesmo horário, mesma consulta
            "profissional": self.profissional.id
        }
        
        response = self.client.put(f"{self.url}{self.consulta.id}/", updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nao_deve_permitir_consultas_passadas(self):
        """
        Teste para validar que não é possível agendar consultas no passado
        """
        past_data = self.data.copy()
        past_data["data"] = (timezone.now() - timezone.timedelta(days=1)).isoformat()
        
        response = self.client.post(self.url, past_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A data da consulta deve ser futura", str(response.data))