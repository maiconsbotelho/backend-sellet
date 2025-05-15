from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    """
    Autenticação personalizada que extrai o access_token do cookie HTTP-only.
    Ideal para cenários onde o token JWT não é enviado via Authorization Header.
    """

    def authenticate(self, request):
        # Tenta obter o token diretamente do cookie (enviado via navegador)
        raw_token = request.COOKIES.get("access_token")
        logger.debug(f"🧪 Token bruto encontrado no cookie: {raw_token}")

        if raw_token is None:
            # Nenhum token presente no cookie: retorna None (DRF tenta outras classes de auth)
            logger.warning("⚠️ Nenhum access_token presente no cookie.")
            return None

        try:
            # Valida a estrutura do token
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            logger.error(f"❌ Erro ao validar token JWT: {e}")
            raise AuthenticationFailed("Token inválido ou expirado.")
        
        logger.debug("✅ Token JWT validado com sucesso.")
        user = self.get_user(validated_token)
        logger.debug(f"🔐 Usuário autenticado via token: {user}")

        # Associa o token validado a um usuário
        return user, validated_token
