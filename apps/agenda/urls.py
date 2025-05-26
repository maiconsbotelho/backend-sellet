from rest_framework.routers import DefaultRouter
from apps.agenda.views.expediente import HorarioExpedienteViewSet
from apps.agenda.views.agendamento import AgendamentoViewSet
from django.urls import path, include
from apps.agenda.views.expediente import horarios_estabelecimento

router = DefaultRouter()
router.register(r'expediente', HorarioExpedienteViewSet, basename='expediente')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamentos')

urlpatterns = [
    path('horarios-estabelecimento/', horarios_estabelecimento, name='horarios-estabelecimento'),
    path('', include(router.urls)),
]