from rest_framework.routers import DefaultRouter
from .views import ServicoViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'', ServicoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
