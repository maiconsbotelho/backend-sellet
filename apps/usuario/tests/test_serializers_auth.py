from django.test import TestCase
from rest_framework import serializers  # <-- Importar o ValidationError correto

from apps.usuario.models import Usuario, TipoUsuario
from apps.usuario.auth.serializers_auth import CustomTokenObtainPairSerializer


class CustomTokenObtainPairSerializerTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="user@test.com",
            password="senha123",
            nome_completo="Usuário Teste",
            tipo=TipoUsuario.CLIENTE
        )

    def test_login_valido_retorna_tokens(self):
        """Deve retornar access e refresh tokens para login válido."""
        data = {"email": "user@test.com", "password": "senha123"}
        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIn("access", serializer.validated_data)
        self.assertIn("refresh", serializer.validated_data)

    def test_login_invalido_levanta_erro(self):
        """Deve levantar ValidationError para credenciais inválidas."""
        data = {"email": "user@test.com", "password": "senha_errada"}
        serializer = CustomTokenObtainPairSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_email_ou_senha_faltando(self):
        """Deve levantar ValidationError se email ou senha faltarem."""
        data = {"email": "", "password": ""}
        serializer = CustomTokenObtainPairSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
