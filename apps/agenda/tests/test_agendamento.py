from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from datetime import date, time, timedelta

from apps.usuario.models import Usuario, TipoUsuario
from apps.servicos.models import Servico
from apps.agenda.models import Agendamento, HorarioExpediente, Horario


class AgendamentoTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.profissional = Usuario.objects.create_user(
            email="prof@test.com",
            password="senha123",
            nome_completo="Profissional Teste",
            tipo=TipoUsuario.PROFISSIONAL
        )
        self.cliente = Usuario.objects.create_user(
            email="cliente@test.com",
            password="senha123",
            nome_completo="Cliente Teste",
            tipo=TipoUsuario.CLIENTE
        )
        self.servico = Servico.objects.create(
            nome="Corte",
            preco=100,
            duracao=timedelta(minutes=30)
        )
        self.servico.profissionais.add(self.profissional)  # Vincula o serviço ao profissional

        # Cria expediente para o profissional
        self.horario_09 = Horario.objects.create(horario=time(9, 0))
        self.horario_0930 = Horario.objects.create(horario=time(9, 30))
        self.expediente = HorarioExpediente.objects.create(
            profissional=self.profissional,
            dia_semana=0
        )
        self.expediente.horarios.add(self.horario_09, self.horario_0930)

    def test_criar_agendamento_valido(self):
        url = reverse('agendamentos-list')
        payload = {
            "cliente": self.cliente.id,
            "profissional": self.profissional.id,
            "servico": self.servico.id,
            "data": date.today().isoformat(),
            "hora": "09:00"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_nao_permitir_agendamento_fora_expediente(self):
        url = reverse('agendamentos-list')
        payload = {
            "cliente": self.cliente.id,
            "profissional": self.profissional.id,
            "servico": self.servico.id,
            "data": date.today().isoformat(),
            "hora": "10:00"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("expediente", str(response.data).lower())

    def test_nao_permitir_conflito_profissional(self):
        Agendamento.objects.create(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data=date.today(),
            hora=time(9, 0)
        )

        url = reverse('agendamentos-list')
        payload = {
            "cliente": self.cliente.id,
            "profissional": self.profissional.id,
            "servico": self.servico.id,
            "data": date.today().isoformat(),
            "hora": "09:00"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("conflito", str(response.data).lower())

    def test_nao_permitir_conflito_cliente(self):
        outro_profissional = Usuario.objects.create_user(
            email="prof2@test.com",
            password="senha123",
            nome_completo="Outro Profissional",
            tipo=TipoUsuario.PROFISSIONAL
        )
        self.servico.profissionais.add(outro_profissional)
        HorarioExpediente.objects.create(
            profissional=outro_profissional,
            dia_semana=0
        ).horarios.add(self.horario_09)

        Agendamento.objects.create(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data=date.today(),
            hora=time(9, 0)
        )

        url = reverse('agendamentos-list')
        payload = {
            "cliente": self.cliente.id,
            "profissional": outro_profissional.id,
            "servico": self.servico.id,
            "data": date.today().isoformat(),
            "hora": "09:00"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("conflito", str(response.data).lower())

    # 🧪 Testes adicionais para o endpoint /agenda
    def test_agenda_endpoint_retorna_dados(self):
        url = reverse('agendamentos-agenda')
        data_inicial = date.today().isoformat()
        data_final = (date.today() + timedelta(days=6)).isoformat()
        response = self.client.get(f"{url}?profissional={self.profissional.id}&data_inicial={data_inicial}&data_final={data_final}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, list))

    def test_agenda_endpoint_sem_profissional(self):
        url = reverse('agendamentos-agenda')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("profissional", str(response.data).lower())

    def test_atualizar_agendamento_valido(self):
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data=date.today(),
            hora=time(9, 0)
        )
        url = reverse('agendamentos-detail', args=[agendamento.id])
        novo_payload = {
            "cliente": self.cliente.id,
            "profissional": self.profissional.id,
            "servico": self.servico.id,
            "data": date.today().isoformat(),
            "hora": "09:30"
        }
        response = self.client.put(url, novo_payload, format='json')
        self.assertEqual(response.status_code, 200)
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.hora.strftime("%H:%M"), "09:30")

    def test_deletar_agendamento(self):
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data=date.today(),
            hora=time(9, 0)
        )
        url = reverse('agendamentos-detail', args=[agendamento.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Agendamento.objects.count(), 0)

