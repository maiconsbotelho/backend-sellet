from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import time, date, timedelta

from apps.usuario.models import Usuario, TipoUsuario
from apps.agenda.models import Horario, HorarioExpediente, Agendamento
from apps.servicos.models import Servico


class HorarioExpedienteTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.profissional = Usuario.objects.create_user(
            email="prof@test.com",
            password="senha123",
            nome_completo="Profissional Teste",
            tipo=TipoUsuario.PROFISSIONAL
        )

        self.horario_09 = Horario.objects.create(horario=time(9, 0))
        self.horario_0930 = Horario.objects.create(horario=time(9, 30))

        self.servico = Servico.objects.create(
            nome="Corte",
            preco=100,
            duracao=timedelta(minutes=30)
        )
        self.servico.profissionais.add(self.profissional)

    def test_criar_horario_expediente(self):
        url = reverse('expediente-list')
        payload = {
            "profissional": self.profissional.id,
            "dia_semana": 0,
            "inicio": "09:00",
            "fim": "09:30"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(HorarioExpediente.objects.count(), 1)

        expediente = HorarioExpediente.objects.first()
        self.assertEqual(expediente.horarios.count(), 2)

    def test_por_profissional_view(self):
        HorarioExpediente.objects.create(profissional=self.profissional, dia_semana=0)
        url = reverse('expediente-por-profissional') + f"?profissional={self.profissional.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_horarios_disponiveis_view(self):
        expediente = HorarioExpediente.objects.create(
            profissional=self.profissional,
            dia_semana=0
        )
        expediente.horarios.add(self.horario_09, self.horario_0930)

        cliente = Usuario.objects.create_user(
            email="cliente@test.com",
            password="senha123",
            nome_completo="Cliente Teste",
            tipo=TipoUsuario.CLIENTE
        )

        Agendamento.objects.create(
            cliente=cliente,
            profissional=self.profissional,
            servico=self.servico,
            data=date(2025, 5, 26),
            hora=time(9, 0)
        )

        url = reverse('expediente-horarios-disponiveis', args=[expediente.id]) + "?data=2025-05-26"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        horarios = {h['horario']: h['ocupado'] for h in response.data}
        self.assertTrue(horarios['09:00'])
        self.assertFalse(horarios['09:30'])
