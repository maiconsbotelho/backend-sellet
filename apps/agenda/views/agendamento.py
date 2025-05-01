from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from datetime import datetime, timedelta, time
from collections import defaultdict # Para agrupar horários ocupados
from apps.agenda.models import Agendamento, HorarioExpediente, Horario
from apps.servicos.models import Servico # Importar Servico
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
        profissional_id = request.query_params.get('profissional')
        data_inicial_str = request.query_params.get('data_inicial')
        data_final_str = request.query_params.get('data_final')

        if not profissional_id:
            return Response({"erro": "O ID do profissional é obrigatório."}, status=400)

        try:
            profissional_id = int(profissional_id)
        except ValueError:
            return Response({"erro": "O ID do profissional deve ser um número inteiro."}, status=400)

        try:
            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d').date() if data_inicial_str else datetime.today().date()
            data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date() if data_final_str else data_inicial + timedelta(days=6)
            if data_final < data_inicial:
                 return Response({"erro": "A data final não pode ser anterior à data inicial."}, status=400)
        except ValueError:
            return Response({"erro": "Formato de data inválido. Use 'YYYY-MM-DD'."}, status=400)

        # --- Obter Expedientes ---
        expedientes = HorarioExpediente.objects.filter(
            profissional_id=profissional_id,
            dia_semana__in=[(data_inicial + timedelta(days=i)).weekday() for i in range((data_final - data_inicial).days + 1)]
        ).prefetch_related('horarios')
        horarios_por_dia = {exp.dia_semana: {h.horario for h in exp.horarios.all()} for exp in expedientes}

        # --- Obter Agendamentos e Calcular Slots Ocupados ---
        agendamentos = Agendamento.objects.filter(
            profissional_id=profissional_id,
            data__range=[data_inicial, data_final]
        ).select_related('cliente', 'servico') # Inclui servico para pegar duração

        # Estrutura para guardar todos os slots ocupados por data e o agendamento que os originou
        # Ex: slots_ocupados['2025-05-01'][time(9,0)] = agendamento_obj
        slots_ocupados = defaultdict(dict)

        for ag in agendamentos:
            inicio_ag_dt = ag.hora_inicio_dt
            fim_ag_dt = ag.hora_fim_dt

            if not inicio_ag_dt or not fim_ag_dt:
                 print(f"Aviso: Agendamento ID {ag.id} com dados inválidos para cálculo de duração.")
                 continue # Pula agendamento inválido

            data_str = ag.data.strftime('%Y-%m-%d')
            horario_atual_dt = inicio_ag_dt
            while horario_atual_dt < fim_ag_dt:
                slot_time = horario_atual_dt.time()
                # Guarda o agendamento que iniciou a ocupação deste slot
                # Se já estiver ocupado por outro, a lógica de validação deveria ter impedido
                if slot_time not in slots_ocupados[data_str]:
                     slots_ocupados[data_str][slot_time] = ag
                else:
                     # Isso indica um problema na validação ou dados inconsistentes
                     print(f"Aviso: Slot {data_str} {slot_time.strftime('%H:%M')} já ocupado por {slots_ocupados[data_str][slot_time].id}, tentando marcar por {ag.id}")
                horario_atual_dt += timedelta(minutes=30)


        # --- Estruturar a Resposta da Agenda ---
        agenda_resposta = []
        # Considera apenas os horários que realmente existem no expediente de algum dia/profissional
        # Ou busca todos os horários base se preferir mostrar a grade completa
        todos_horarios_possiveis = Horario.objects.all().order_by('horario')

        for horario_obj in todos_horarios_possiveis:
            horario_time = horario_obj.horario
            linha = {"horario": horario_time.strftime('%H:%M')}

            for dia_offset in range((data_final - data_inicial).days + 1):
                dia_atual = data_inicial + timedelta(days=dia_offset)
                dia_semana = dia_atual.weekday()
                data_str = dia_atual.strftime('%Y-%m-%d')

                # Verifica se está dentro do expediente para este dia e horário
                esta_no_expediente = dia_semana in horarios_por_dia and horario_time in horarios_por_dia[dia_semana]

                # Verifica se o slot está marcado como ocupado
                agendamento_origem = slots_ocupados[data_str].get(horario_time)

                if agendamento_origem:
                    # Slot Ocupado (independente de estar ou não no expediente - pode ter sido marcado antes de mudança no expediente)
                    linha[data_str] = {
                        "ocupado": True,
                        "agendamento_id": agendamento_origem.id,
                        "cliente_id": agendamento_origem.cliente.id,
                        "nome_cliente": agendamento_origem.cliente.nome,
                        "servico_id": agendamento_origem.servico.id,
                        "servico_nome": agendamento_origem.servico.nome
                    }
                elif esta_no_expediente:
                    # Slot Livre dentro do expediente
                    linha[data_str] = {"ocupado": False}
                else:
                    # Fora do Expediente e não ocupado por agendamento pré-existente
                    linha[data_str] = {"ocupado": None}

            agenda_resposta.append(linha)

        return Response(agenda_resposta)
