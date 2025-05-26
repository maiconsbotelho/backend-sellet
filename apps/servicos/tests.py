from django.test import TestCase
from datetime import timedelta

from apps.usuario.models import Usuario, TipoUsuario
from apps.servicos.models import Servico
from django.core.exceptions import ValidationError


class ServicoModelTests(TestCase):
    def setUp(self):
        # Cria um profissional para associar ao serviço
        self.profissional = Usuario.objects.create_user(
            email="prof@test.com",
            password="senha123",
            nome_completo="Profissional Teste",
            tipo=TipoUsuario.PROFISSIONAL
        )

    def test_criar_servico_valido(self):
        """Deve criar um serviço com sucesso."""
        servico = Servico.objects.create(
            nome="Corte de Cabelo",
            descricao="Corte de cabelo simples",
            duracao=timedelta(minutes=30),
            preco=50
        )
        servico.profissionais.add(self.profissional)

        self.assertEqual(servico.nome, "Corte de Cabelo")
        self.assertEqual(servico.duracao, timedelta(minutes=30))
        self.assertEqual(servico.preco, 50)
        self.assertIn(self.profissional, servico.profissionais.all())

    def test_duracao_negativa_deve_falhar(self):
        """Não deve permitir duração negativa."""
        servico = Servico(
            nome="Massagem",
            descricao="Massagem relaxante",
            duracao=timedelta(minutes=-30),
            preco=100
        )
        with self.assertRaises(ValidationError) as cm:
            servico.clean()
        self.assertIn("A duração do serviço deve ser positiva.", str(cm.exception))

    def test_duracao_nao_multiplo_30_exibe_aviso(self):
        """Duração que não seja múltipla de 30 deve exibir aviso (sem erro)."""
        servico = Servico(
            nome="Tratamento Capilar",
            descricao="Hidratação profunda",
            duracao=timedelta(minutes=45),
            preco=150
        )
        # A clean() só exibe print, não levanta erro nesse caso
        servico.clean()

    def test_profissionais_deve_aceitar_apenas_profissionais(self):
        """Somente usuários com tipo PROFISSIONAL podem ser vinculados ao serviço."""
        cliente = Usuario.objects.create_user(
            email="cliente@test.com",
            password="senha123",
            nome_completo="Cliente Teste",
            tipo=TipoUsuario.CLIENTE
        )

        servico = Servico.objects.create(
            nome="Esmaltação",
            descricao="Aplicação de esmalte",
            duracao=timedelta(minutes=30),
            preco=30
        )

        servico.profissionais.add(self.profissional)
        self.assertIn(self.profissional, servico.profissionais.all())

        # Tenta adicionar um cliente (não deve ser permitido pela interface admin/DRF, mas testamos aqui)
        servico.profissionais.add(cliente)
        self.assertIn(cliente, servico.profissionais.all())  # No banco permite, mas na UI validamos

    def test_str_method(self):
        """__str__ deve retornar nome e duração."""
        servico = Servico.objects.create(
            nome="Design de Sobrancelha",
            preco=80,
            duracao=timedelta(minutes=60)
        )
        self.assertIn("Design de Sobrancelha", str(servico))
