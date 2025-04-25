from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from datetime import datetime
from apps.agenda.models import Agendamento, HorarioExpediente
from apps.agenda.serializers import HorarioExpedienteSerializer

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
        # Obtém o expediente pelo ID
        expediente = self.get_object()

        # Obtém a data passada como parâmetro na query string
        data = request.query_params.get('data')
        if not data:
            return Response({"erro": "A data é obrigatória. Use o parâmetro 'data' na URL."}, status=400)

        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            return Response({"erro": "Formato de data inválido. Use o formato 'YYYY-MM-DD'."}, status=400)

        # Obtém todos os horários do expediente
        horarios = expediente.horarios.all()

        # Obtém os horários ocupados para o profissional na data especificada
        horarios_ocupados = Agendamento.objects.filter(
            profissional=expediente.profissional,
            data=data_obj
        ).values_list('hora', flat=True)

        # Classifica os horários como disponíveis ou ocupados
        resultado = []
        for horario in horarios:
            resultado.append({
                "horario": horario.horario.strftime('%H:%M'),
                "ocupado": horario.horario in horarios_ocupados
            })

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

        # Filtra os expedientes pelo ID do profissional
        expedientes = HorarioExpediente.objects.filter(profissional_id=profissional_id)
        serializer = self.get_serializer(expedientes, many=True)
        return Response(serializer.data)