from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.usuario.models import Usuario, TipoUsuario


class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(
            email="user@test.com",
            password="senha123",
            nome_completo="Usuário Teste",
            tipo=TipoUsuario.CLIENTE
        )

    def test_login_com_credenciais_validas(self):
        url = reverse("token_obtain_pair")
        payload = {"email": "user@test.com", "password": "senha123"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica se os cookies foram definidos corretamente
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        # O corpo da resposta não contém os tokens
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_login_com_credenciais_invalidas(self):
        url = reverse("token_obtain_pair")
        payload = {"email": "user@test.com", "password": "senhaerrada"}
        response = self.client.post(url, payload, format="json")

        # DRF com SimpleJWT retorna 400 para login inválido
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_refresh_token_valido(self):
        # Login para obter cookies
        login_url = reverse("token_obtain_pair")
        login_response = self.client.post(login_url, {"email": "user@test.com", "password": "senha123"}, format="json")

        self.assertIn("refresh_token", login_response.cookies)

        # Faz refresh usando o cookie
        refresh_url = reverse("token_refresh")
        self.client.cookies = login_response.cookies  # Carrega cookies no client

        response = self.client.post(refresh_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # O access_token é retornado no body pelo SimpleJWT
        self.assertIn("access", response.data)

    def test_refresh_token_ausente(self):
        url = reverse("token_refresh")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_logout_apaga_cookies(self):
        # Login para obter cookies
        login_url = reverse("token_obtain_pair")
        login_response = self.client.post(login_url, {"email": "user@test.com", "password": "senha123"}, format="json")

        self.assertIn("access_token", login_response.cookies)

        # Logout
        logout_url = reverse("logout")
        self.client.cookies = login_response.cookies
        response = self.client.post(logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        # Checa se os cookies foram apagados (expirados)
        self.assertIn("access_token", response.cookies)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["refresh_token"].value, "")

    def test_me_view_autenticado(self):
        # Login para obter cookies
        login_url = reverse("token_obtain_pair")
        login_response = self.client.post(login_url, {"email": "user@test.com", "password": "senha123"}, format="json")
        self.client.cookies = login_response.cookies

        me_url = reverse("me")
        response = self.client.get(me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@test.com")

    def test_me_view_sem_autenticacao(self):
        me_url = reverse("me")
        response = self.client.get(me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
