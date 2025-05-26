from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from collections import defaultdict

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
        Retorna a agenda semanal ou diária de um profissional,
        considerando a duração dos serviços para marcar horários ocupados.
        """
        # --- Parâmetros obrigatórios e validação ---
        profissional_id = request.query_params.get('profissional')
        if not profissional_id:
            return Response({"erro": "O ID do profissional é obrigatório."}, status=400)

        try:
            profissional_id = int(profissional_id)
        except ValueError:
            return Response({"erro": "O ID do profissional deve ser um número inteiro."}, status=400)

        try:
            data_inicial_str = request.query_params.get('data_inicial')
            data_final_str = request.query_params.get('data_final')

            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d').date() if data_inicial_str else datetime.today().date()
            data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date() if data_final_str else data_inicial + timedelta(days=6)

            if data_final < data_inicial:
                return Response({"erro": "A data final não pode ser anterior à data inicial."}, status=400)

        except ValueError:
            return Response({"erro": "Formato de data inválido. Use 'YYYY-MM-DD'."}, status=400)

        # --- Buscar Expediente ---
        dias_semana = [(data_inicial + timedelta(days=i)).weekday() for i in range((data_final - data_inicial).days + 1)]
        expedientes = HorarioExpediente.objects.filter(
            profissional_id=profissional_id,
            dia_semana__in=dias_semana
        ).prefetch_related('horarios')

        horarios_por_dia = {
            exp.dia_semana: {h.horario for h in exp.horarios.all()}
            for exp in expedientes
        }

        # --- Buscar Agendamentos Existentes ---
        agendamentos = Agendamento.objects.filter(
            profissional_id=profissional_id,
            data__range=[data_inicial, data_final]
        ).select_related('cliente', 'servico')

        slots_ocupados = defaultdict(dict)

        for ag in agendamentos:
            inicio_dt = ag.hora_inicio_dt
            fim_dt = ag.hora_fim_dt

            if not inicio_dt or not fim_dt:
                print(f"Aviso: Agendamento ID {ag.id} com dados inválidos.")
                continue

            data_str = ag.data.strftime('%Y-%m-%d')
            horario_atual = inicio_dt
            while horario_atual < fim_dt:
                slot_time = horario_atual.time()
                if slot_time not in slots_ocupados[data_str]:
                    slots_ocupados[data_str][slot_time] = ag
                else:
                    print(f"Aviso: Slot {data_str} {slot_time.strftime('%H:%M')} já ocupado por {slots_ocupados[data_str][slot_time].id}, tentando marcar por {ag.id}")
                horario_atual += timedelta(minutes=30)

        # --- Montar a Resposta ---
        agenda_resposta = []
        horarios_base = Horario.objects.all().order_by('horario')

        for horario_obj in horarios_base:
            horario_time = horario_obj.horario
            linha = {"horario": horario_time.strftime('%H:%M')}

            for i in range((data_final - data_inicial).days + 1):
                dia_atual = data_inicial + timedelta(days=i)
                dia_semana = dia_atual.weekday()
                data_str = dia_atual.strftime('%Y-%m-%d')

                no_expediente = dia_semana in horarios_por_dia and horario_time in horarios_por_dia[dia_semana]
                agendamento = slots_ocupados[data_str].get(horario_time)

                if agendamento:
                    linha[data_str] = {
                        "ocupado": True,
                        "agendamento_id": agendamento.id,
                        "cliente_id": agendamento.cliente.id,
                        "nome_cliente": str(agendamento.cliente),
                        "servico_id": agendamento.servico.id,
                        "servico_nome": agendamento.servico.nome
                    }
                elif no_expediente:
                    linha[data_str] = {"ocupado": False}
                else:
                    linha[data_str] = {"ocupado": None}

            agenda_resposta.append(linha)

        return Response(agenda_resposta)
    

 
