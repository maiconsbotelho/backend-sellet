from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet
from .auth.views_auth import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
)

# Roteamento principal dos usuários
router = DefaultRouter()
router.register(r'', UsuarioViewSet)

urlpatterns = [
    # Autenticação
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),

    # CRUD de usuários
    path('', include(router.urls)),
]
