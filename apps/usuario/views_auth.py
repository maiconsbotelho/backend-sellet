from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings  # para acessar DEBUG

from .serializers_auth import CustomTokenObtainPairSerializer
from .serializers import UsuarioSerializer


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh = response.data.get("refresh")
            access = response.data.get("access")

            # Cookies com suporte a domínios diferentes via HTTPS
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="None",
                path="/api/usuario/refresh/"
                max_age=7 * 24 * 60 * 60,  # 7 dias
            )
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="None",
                path="/"
                max_age=30 * 60,  # 30 minutos
            )

            # Cabeçalhos CORS explícitos (importante para o login funcionar via frontend externo)
            # response["Access-Control-Allow-Credentials"] = "true"
            # response["Access-Control-Allow-Origin"] = "https://hml.selletesmalteria.com.br"

            # Remove os tokens do corpo da resposta
            response.data.pop("refresh", None)
            response.data.pop("access", None)

        return response


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token não encontrado no cookie."},
                status=401
            )

        request.data["refresh"] = refresh_token
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request):
        response = Response(
            {"detail": "Logout realizado com sucesso"},
            status=status.HTTP_200_OK
        )
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/api/usuario/refresh/")
        return response


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
