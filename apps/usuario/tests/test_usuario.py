from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import Usuario, TipoUsuario
from ..serializers import UsuarioCreateSerializer


class TesteModeloUsuario(TestCase):
    """Testes para o modelo Usuario."""

    def test_criar_usuario_sucesso(self):
        """Deve criar um usuário com sucesso."""
        user = Usuario.objects.create_user(
            email="user@test.com",
            password="pass123",
            nome_completo="Usuário Teste",
            tipo=TipoUsuario.CLIENTE
        )
        self.assertIsInstance(user, Usuario)
        self.assertEqual(user.email, "user@test.com")
        self.assertEqual(user.nome_completo, "Usuário Teste")
        self.assertEqual(user.tipo, TipoUsuario.CLIENTE)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("pass123"))

    def test_criar_usuario_sem_email(self):
        """Deve falhar ao criar usuário sem email."""
        with self.assertRaises(ValueError) as cm:
            Usuario.objects.create_user(
                email="",
                password="pass123",
                nome_completo="Sem Email",
                tipo=TipoUsuario.CLIENTE
            )
        self.assertEqual(str(cm.exception), "O campo email é obrigatório")

    def test_criar_superusuario_sucesso(self):
        """Deve criar um superusuário com sucesso."""
        su = Usuario.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)
        self.assertEqual(su.tipo, TipoUsuario.ADMIN)
        self.assertEqual(su.nome_completo, "Administrador")

    def test_criar_superusuario_tipo_invalido(self):
        """Deve falhar se tentar criar superusuário com tipo inválido."""
        with self.assertRaises(ValueError) as cm:
            Usuario.objects.create_superuser(
                email="bad@test.com",
                password="badpass",
                tipo=TipoUsuario.CLIENTE
            )
        self.assertIn("O superusuário deve ter tipo ADMIN", str(cm.exception))

    def test_metodo_str(self):
        """Método __str__ deve exibir nome e tipo do usuário."""
        user = Usuario.objects.create_user(
            email="str@test.com",
            password="pass123",
            nome_completo="Teste String",
            tipo=TipoUsuario.PROFISSIONAL
        )
        esperado = f"{user.nome_completo}"

        self.assertEqual(str(user), esperado)


class TesteUsuarioCreateSerializer(TestCase):
    """Testes para o serializer UsuarioCreateSerializer."""

    def test_tipo_aceita_valores_validos(self):
        """Deve aceitar CLIENTE e PROFISSIONAL no tipo."""
        dados = {
            "email": "new@test.com",
            "nome_completo": "Novo Usuário",
            "tipo": TipoUsuario.CLIENTE,
            "password": "novasenha"
        }
        serializer = UsuarioCreateSerializer(data=dados)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('tipo', serializer.errors)

    def test_tipo_rejeita_valor_invalido(self):
        """Deve rejeitar ADMIN no tipo para criação via serializer."""
        dados = {
            "email": "admin2@test.com",
            "nome_completo": "Usuário Admin",
            "tipo": TipoUsuario.ADMIN,
            "password": "adminpass"
        }
        serializer = UsuarioCreateSerializer(data=dados)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tipo', serializer.errors)
        self.assertIn("Tipo de usuário inválido", serializer.errors['tipo'][0])

    def test_criar_usuario_via_serializer(self):
        """Deve criar usuário via serializer com sucesso."""
        dados = {
            "email": "create@test.com",
            "nome_completo": "Usuário Criado",
            "tipo": TipoUsuario.PROFISSIONAL,
            "password": "securepass"
        }
        serializer = UsuarioCreateSerializer(data=dados)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsInstance(user, Usuario)
        self.assertEqual(user.email, dados['email'])
        self.assertEqual(user.nome_completo, dados['nome_completo'])
        self.assertEqual(user.tipo, dados['tipo'])
        self.assertTrue(user.check_password(dados['password']))
