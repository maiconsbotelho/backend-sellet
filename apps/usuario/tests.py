from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Usuario, TipoUsuario
from .serializers import UsuarioCreateSerializer

# filepath: backend-sellet/apps/usuario/test_tests.py

class UsuarioModelTests(TestCase):
    def test_create_user_success(self):
        user = Usuario.objects.create_user(
            email="user@test.com",
            password="pass123",
            nome_completo="User Test",
            tipo=TipoUsuario.CLIENTE
        )
        self.assertIsInstance(user, Usuario)
        self.assertEqual(user.email, "user@test.com")
        self.assertEqual(user.nome_completo, "User Test")
        self.assertEqual(user.tipo, TipoUsuario.CLIENTE)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("pass123"))

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError) as cm:
            Usuario.objects.create_user(
                email="",
                password="pass123",
                nome_completo="No Email",
                tipo=TipoUsuario.CLIENTE
            )
        self.assertEqual(str(cm.exception), "O campo email é obrigatório")

    def test_create_superuser_success(self):
        su = Usuario.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)
        self.assertEqual(su.tipo, TipoUsuario.ADMIN)
        self.assertEqual(su.nome_completo, "Administrador")

    def test_create_superuser_invalid_tipo(self):
        with self.assertRaises(ValueError) as cm:
            Usuario.objects.create_superuser(
                email="bad@test.com",
                password="badpass",
                tipo=TipoUsuario.CLIENTE
            )
        self.assertIn("O superusuário deve ter tipo ADMIN", str(cm.exception))

    def test_str_method(self):
        user = Usuario.objects.create_user(
            email="str@test.com",
            password="pass123",
            nome_completo="Str Test",
            tipo=TipoUsuario.PROFISSIONAL
        )
        expected = f"Str Test ({user.get_tipo_display()})"
        self.assertEqual(str(user), expected)

class UsuarioCreateSerializerTests(TestCase):
    def test_validate_tipo_accepts_valid(self):
        data = {
            "email": "new@test.com",
            "nome_completo": "New User",
            "tipo": TipoUsuario.CLIENTE,
            "password": "newpass"
        }
        serializer = UsuarioCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('tipo', serializer.errors)

    def test_validate_tipo_rejects_invalid(self):
        data = {
            "email": "admin2@test.com",
            "nome_completo": "Admin User",
            "tipo": TipoUsuario.ADMIN,
            "password": "adminpass"
        }
        serializer = UsuarioCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tipo', serializer.errors)
        self.assertIn("Tipo de usuário inválido.", serializer.errors['tipo'])

    def test_create_user_via_serializer(self):
        data = {
            "email": "create@test.com",
            "nome_completo": "Create User",
            "tipo": TipoUsuario.PROFISSIONAL,
            "password": "securepass"
        }
        serializer = UsuarioCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsInstance(user, Usuario)
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.nome_completo, data['nome_completo'])
        self.assertEqual(user.tipo, data['tipo'])
        self.assertTrue(user.check_password(data['password']))