from django.test import TestCase
from datetime import date, time, timedelta
from apps.agenda.models import Agendamento, Horario, HorarioExpediente
from apps.agenda.serializers.agendamento import AgendamentoSerializer
from apps.usuario.models import Usuario, TipoUsuario
from apps.servicos.models import Servico


class AgendamentoSerializerTests(TestCase):
    def setUp(self):
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
        self.servico.profissionais.add(self.profissional)

        self.horario = Horario.objects.create(horario=time(9, 0))
        expediente = HorarioExpediente.objects.create(profissional=self.profissional, dia_semana=0)
        expediente.horarios.add(self.horario)

    def test_serializer_valido(self):
        data = {
            "cliente": self.cliente.id,
            "profissional": self.profissional.id,
            "servico": self.servico.id,
            "data": date.today(),
            "hora": time(9, 0)
        }
        serializer = AgendamentoSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_invalido_sem_expediente(self):
        data = {
            "cliente": self.cliente.id,
            "profissional": self.profissional.id,
            "servico": self.servico.id,
            "data": date.today(),
            "hora": time(10, 0)
        }
        serializer = AgendamentoSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("expediente", str(serializer.errors).lower())
