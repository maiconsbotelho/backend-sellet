from rest_framework.routers import DefaultRouter
from apps.agenda.views.expediente import HorarioExpedienteViewSet
from apps.agenda.views.agendamento import AgendamentoViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'expediente', HorarioExpedienteViewSet, basename='expediente')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamentos')

urlpatterns = [
    path('', include(router.urls)),
]