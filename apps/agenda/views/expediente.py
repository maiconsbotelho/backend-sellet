from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from apps.agenda.models import HorarioExpediente, Agendamento
from apps.agenda.serializers import HorarioExpedienteSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.agenda.models.expediente import HORARIOS_DISPONIVEIS


class HorarioExpedienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Horário de Expediente.
    Permite listar, criar, atualizar e excluir horários de expediente.
    """
    queryset = HorarioExpediente.objects.all()
    serializer_class = HorarioExpedienteSerializer

    @action(detail=True, methods=['get'])
    def horarios_disponiveis(self, request, pk=None):
        """
        Retorna os horários disponíveis e ocupados de um profissional em uma data específica.
        """
        expediente = self.get_object()
        data = request.query_params.get('data')

        if not data:
            return Response({"erro": "A data é obrigatória. Use o parâmetro 'data' na URL."}, status=400)

        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            return Response({"erro": "Formato de data inválido. Use o formato 'YYYY-MM-DD'."}, status=400)

        horarios = expediente.horarios.all()
        horarios_ocupados = Agendamento.objects.filter(
            profissional=expediente.profissional,
            data=data_obj
        ).values_list('hora', flat=True)

        resultado = [
            {
                "horario": h.horario.strftime('%H:%M'),
                "ocupado": h.horario in horarios_ocupados
            }
            for h in horarios
        ]

        return Response(resultado)

    @action(detail=False, methods=['get'])
    def por_profissional(self, request):
        """
        Retorna os horários de expediente de um profissional específico.
        """
        profissional_id = request.query_params.get('profissional')

        if not profissional_id:
            return Response({"erro": "O ID do profissional é obrigatório."}, status=400)

        try:
            profissional_id = int(profissional_id)
        except ValueError:
            return Response({"erro": "O ID do profissional deve ser um número inteiro."}, status=400)

        expedientes = HorarioExpediente.objects.filter(profissional_id=profissional_id)
        serializer = self.get_serializer(expedientes, many=True)
        return Response(serializer.data)
    


@api_view(['GET'])
def horarios_estabelecimento(request):
    """
    Retorna a lista de horários disponíveis do estabelecimento.
    """
    return Response([h[1] for h in HORARIOS_DISPONIVEIS])
