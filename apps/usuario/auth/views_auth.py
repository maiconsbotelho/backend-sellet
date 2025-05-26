import logging
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework_simplejwt.tokens import RefreshToken

from ..auth.serializers_auth import CustomTokenObtainPairSerializer
from ..serializers import UsuarioSerializer

logger = logging.getLogger(__name__)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Login via JWT, usando cookies HTTP-only para armazenar access/refresh tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.debug("🔐 Requisição de login recebida.")
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            refresh = response.data.get("refresh")
            access = response.data.get("access")
            logger.debug("✔️ Login bem-sucedido. Tokens gerados.")

            # Configura os cookies
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="None",
                path="/api/usuario/refresh/",
                max_age=7 * 24 * 60 * 60,  # 7 dias
            )
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="None",
                path="/",
                max_age=30 * 60,  # 30 minutos
            )
            logger.debug("🍪 Cookies de autenticação setados.")

            # Remove os tokens do corpo da resposta
            response.data.pop("refresh", None)
            response.data.pop("access", None)
        else:
            logger.warning(f"❌ Falha no login. Status: {response.status_code}")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Gera novo access token a partir do refresh token armazenado no cookie.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        logger.debug(f"♻️ Tentativa de refresh. Token encontrado? {bool(refresh_token)}")

        if not refresh_token:
            logger.error("❌ Refresh token não encontrado no cookie.")
            return Response(
                {"detail": "Refresh token não encontrado no cookie."},
                status=401
            )

        request.data["refresh"] = refresh_token
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Realiza logout, removendo os cookies de autenticação.
    """
    def post(self, request):
        logger.debug(f"🚪 Logout iniciado para usuário: {request.user}")

        response = Response(
            {"detail": "Logout realizado com sucesso"},
            status=status.HTTP_200_OK
        )
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/api/usuario/refresh/")
        logger.debug("🧹 Cookies de autenticação removidos.")

        return response


class MeView(APIView):
    """
    Retorna os dados do usuário autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logger.debug("👤 Acessando /me/")
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
