from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers_auth import CustomTokenObtainPairSerializer


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh = response.data.get("refresh")
            access = response.data.get("access")

            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="Strict",
                path="/api/usuario/refresh/"
            )
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="Strict",
                path="/"
            )

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
