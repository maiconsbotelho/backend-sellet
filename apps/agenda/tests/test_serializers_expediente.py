from django.test import TestCase
from datetime import time
from apps.usuario.models import Usuario, TipoUsuario
from apps.agenda.models import Horario, HorarioExpediente
from apps.agenda.serializers.expediente import HorarioExpedienteSerializer, HorarioSerializer


class HorarioExpedienteSerializerTests(TestCase):
    def setUp(self):
        self.profissional = Usuario.objects.create_user(
            email="prof@test.com",
            password="senha123",
            nome_completo="Profissional Teste",
            tipo=TipoUsuario.PROFISSIONAL
        )
        self.horario_09 = Horario.objects.create(horario=time(9, 0))
        self.horario_0930 = Horario.objects.create(horario=time(9, 30))

    def test_criar_horario_expediente_serializer_valido(self):
        data = {
            "profissional": self.profissional.id,
            "dia_semana": 0,
            "inicio": "09:00",
            "fim": "09:30"
        }
        serializer = HorarioExpedienteSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertIsInstance(obj, HorarioExpediente)
        self.assertEqual(obj.horarios.count(), 2)

    def test_falha_sem_inicio_ou_fim(self):
        data = {
            "profissional": self.profissional.id,
            "dia_semana": 0,
        }
        serializer = HorarioExpedienteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("inicio", serializer.errors)
        self.assertIn("fim", serializer.errors)

    def test_falha_inicio_maior_que_fim(self):
        data = {
            "profissional": self.profissional.id,
            "dia_semana": 0,
            "inicio": "10:00",
            "fim": "09:00"
        }
        serializer = HorarioExpedienteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_retorna_horarios_serializados(self):
        expediente = HorarioExpediente.objects.create(profissional=self.profissional, dia_semana=0)
        expediente.horarios.add(self.horario_09, self.horario_0930)
        serializer = HorarioExpedienteSerializer(instance=expediente)
        self.assertIn("horarios", serializer.data)
        self.assertEqual(len(serializer.data["horarios"]), 2)


class HorarioSerializerTests(TestCase):
    def test_serializer_horario_basico(self):
        horario = Horario.objects.create(horario=time(10, 0))
        serializer = HorarioSerializer(instance=horario)
        self.assertEqual(serializer.data["horario"], "10:00")  # Agora ajustado para %H:%M
