from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Autenticação personalizada que extrai o access_token do cookie HTTP-only.
    Ideal para cenários onde o token JWT não é enviado via Authorization Header.
    """

    def authenticate(self, request):
        # Tenta obter o token diretamente do cookie (enviado via navegador)
        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            # Nenhum token presente no cookie: retorna None (DRF tenta outras classes de auth)
            return None

        try:
            # Valida a estrutura do token
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            raise AuthenticationFailed("Token inválido ou expirado.")

        # Associa o token validado a um usuário
        return self.get_user(validated_token), validated_token
