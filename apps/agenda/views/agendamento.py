from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from datetime import datetime, timedelta
from apps.agenda.models import Agendamento, HorarioExpediente, Horario
from apps.agenda.serializers import AgendamentoSerializer

class AgendamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Agendamentos.
    Permite listar, criar, atualizar e excluir agendamentos.
    """
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer

    @action(detail=False, methods=['get'])
    def agenda(self, request):
        """
        Retorna a agenda semanal ou diária de um profissional.
        """
        profissional_id = request.query_params.get('profissional')
        data_inicial = request.query_params.get('data_inicial')
        data_final = request.query_params.get('data_final')

        if not profissional_id:
            return Response({"erro": "O ID do profissional é obrigatório."}, status=400)

        try:
            profissional_id = int(profissional_id)
        except ValueError:
            return Response({"erro": "O ID do profissional deve ser um número inteiro."}, status=400)

        try:
            data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date() if data_inicial else datetime.today().date()
            data_final = datetime.strptime(data_final, '%Y-%m-%d').date() if data_final else data_inicial + timedelta(days=6)
        except ValueError:
            return Response({"erro": "Formato de data inválido. Use o formato 'YYYY-MM-DD'."}, status=400)

        # Obtém os horários de expediente do profissional
        expedientes = HorarioExpediente.objects.filter(profissional_id=profissional_id, dia_semana__in=[
            (data_inicial + timedelta(days=i)).weekday() for i in range((data_final - data_inicial).days + 1)
        ])

        # Mapeia os horários de expediente por dia da semana
        horarios_por_dia = {exp.dia_semana: exp.horarios.all() for exp in expedientes}

        # Obtém os agendamentos do profissional no intervalo de datas
        agendamentos = Agendamento.objects.filter(
            profissional_id=profissional_id,
            data__range=[data_inicial, data_final]
        )

        # Estrutura a resposta
        agenda = []
        for horario in Horario.objects.all().order_by('horario'):
            linha = {"horario": horario.horario.strftime('%H:%M')}
            for dia_offset in range((data_final - data_inicial).days + 1):
                dia = data_inicial + timedelta(days=dia_offset)
                dia_semana = dia.weekday()

                # Verifica se o horário está no expediente
                if dia_semana in horarios_por_dia and horario in horarios_por_dia[dia_semana]:
                    # Verifica se há um agendamento para o horário
                    agendamento = agendamentos.filter(data=dia, hora=horario.horario).first()
                    if agendamento:
                        linha[dia.strftime('%Y-%m-%d')] = {
                            "ocupado": True,
                            "cliente": agendamento.cliente.id,
                            "nome_cliente": str(agendamento.cliente)
                        }
                    else:
                        linha[dia.strftime('%Y-%m-%d')] = {"ocupado": False}
                else:
                    linha[dia.strftime('%Y-%m-%d')] = {"ocupado": None}  # Fora do expediente

            agenda.append(linha)

        return Response(agenda)