import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    """
    Autenticação personalizada via cookie HTTP-only.
    Lê o token JWT do cookie 'access_token' em vez do header Authorization.
    """

    def authenticate(self, request):
        # Obtém o token do cookie (se presente)
        raw_token = request.COOKIES.get("access_token")
        logger.debug(f"🧪 Token bruto encontrado no cookie: {raw_token}")

        if raw_token is None:
            logger.warning("⚠️ Nenhum access_token presente no cookie.")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            logger.error(f"❌ Erro ao validar token JWT: {e}")
            raise AuthenticationFailed("Token inválido ou expirado.")

        user = self.get_user(validated_token)
        logger.debug(f"🔐 Usuário autenticado via token: {user}")

        return (user, validated_token)
