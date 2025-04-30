from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from datetime import datetime, timedelta
from apps.agenda.models import Agendamento, HorarioExpediente, Horario
# Import Servico model if needed for type hinting or direct access, though ForeignKey access works
# from apps.servicos.models import Servico
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
        incluindo detalhes do agendamento se o horário estiver ocupado.
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
            # Define data_inicial como hoje se não for fornecida
            data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date() if data_inicial else datetime.today().date()
            # Define data_final como 6 dias após data_inicial se não for fornecida
            data_final = datetime.strptime(data_final, '%Y-%m-%d').date() if data_final else data_inicial + timedelta(days=6)
        except ValueError:
            return Response({"erro": "Formato de data inválido. Use o formato 'YYYY-MM-DD'."}, status=400)

        # Obtém os horários de expediente do profissional para os dias relevantes
        expedientes = HorarioExpediente.objects.filter(
            profissional_id=profissional_id,
            dia_semana__in=[(data_inicial + timedelta(days=i)).weekday() for i in range((data_final - data_inicial).days + 1)]
        ).prefetch_related('horarios') # Otimiza buscando horários relacionados

        # Mapeia os horários de expediente por dia da semana para acesso rápido
        horarios_por_dia = {exp.dia_semana: set(exp.horarios.all()) for exp in expedientes} # Use set for faster lookups

        # Obtém os agendamentos do profissional no intervalo de datas, otimizando com select_related
        agendamentos = Agendamento.objects.filter(
            profissional_id=profissional_id,
            data__range=[data_inicial, data_final]
        ).select_related('cliente', 'servico') # Busca dados de cliente e serviço na mesma query

        # Estrutura a resposta da agenda
        agenda = []
        # Itera sobre todos os possíveis horários cadastrados, ordenados
        for horario in Horario.objects.all().order_by('horario'):
            linha = {"horario": horario.horario.strftime('%H:%M')}
            # Itera por cada dia no intervalo solicitado
            for dia_offset in range((data_final - data_inicial).days + 1):
                dia = data_inicial + timedelta(days=dia_offset)
                dia_semana = dia.weekday()
                data_str = dia.strftime('%Y-%m-%d') # Formata a data como string para a chave do dicionário

                # Verifica se o profissional trabalha neste dia da semana e neste horário
                if dia_semana in horarios_por_dia and horario in horarios_por_dia[dia_semana]:
                    # Procura por um agendamento existente para este profissional, dia e horário
                    agendamento = agendamentos.filter(data=dia, hora=horario.horario).first()
                    if agendamento:
                        # Se houver agendamento, marca como ocupado e adiciona detalhes
                        linha[data_str] = {
                            "ocupado": True,
                            "agendamento_id": agendamento.id,
                            "cliente_id": agendamento.cliente.id,
                            "nome_cliente": str(agendamento.cliente),
                            "servico_id": agendamento.servico.id,
                            "servico_nome": agendamento.servico.nome
                        }

                    else:
                        # Se não houver agendamento, marca como livre
                        linha[data_str] = {"ocupado": False}
                else:
                    # Se estiver fora do expediente, marca como None (ou outra indicação)
                    linha[data_str] = {"ocupado": None} # Indica que está fora do horário de expediente

            agenda.append(linha) # Adiciona a linha do horário à agenda final

        return Response(agenda)