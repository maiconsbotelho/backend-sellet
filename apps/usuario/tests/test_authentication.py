from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed
from apps.usuario.models import Usuario, TipoUsuario
from apps.usuario.auth.authentication import CookieJWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

class CookieJWTAuthenticationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = Usuario.objects.create_user(
            email="user@test.com",
            password="senha123",
            nome_completo="Usuário Teste",
            tipo=TipoUsuario.CLIENTE
        )
        self.token = str(AccessToken.for_user(self.user))

    def test_autenticar_com_cookie_valido(self):
        request = self.factory.get("/")
        request.COOKIES["access_token"] = self.token

        auth = CookieJWTAuthentication()
        user_auth, token = auth.authenticate(request)

        self.assertEqual(user_auth, self.user)
        self.assertEqual(str(token.payload['user_id']), str(self.user.id))

    def test_falha_sem_cookie(self):
        request = self.factory.get("/")
        auth = CookieJWTAuthentication()
        result = auth.authenticate(request)
        self.assertIsNone(result)

    def test_falha_com_token_invalido(self):
        request = self.factory.get("/")
        request.COOKIES["access_token"] = "token_invalido"

        auth = CookieJWTAuthentication()
        with self.assertRaises(AuthenticationFailed):
            auth.authenticate(request)
