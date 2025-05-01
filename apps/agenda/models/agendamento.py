from django.db import models
from django.core.exceptions import ValidationError
from datetime import time, datetime, timedelta
from apps.agenda.models.expediente import Horario, HorarioExpediente
# from apps.usuario.models import Usuario # Import if needed
from apps.servicos.models import Servico # Import Servico

class Agendamento(models.Model):
    cliente = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, limit_choices_to={'tipo': 'CLIENTE'}, related_name='agendamentos_como_cliente' )
    profissional = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, limit_choices_to={'tipo': 'PROFISSIONAL'}, related_name='agendamentos_como_profissional')
    servico = models.ForeignKey('servicos.Servico', on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()

    def __str__(self):
        hora_formatada = self.hora.strftime('%H:%M')
        return f"{self.data} às {hora_formatada} - {self.cliente} com {self.profissional}"

    @property
    def hora_inicio_dt(self):
        """Retorna o datetime de início do agendamento."""
        if not self.data or not self.hora:
            return None
        return datetime.combine(self.data, self.hora)

    @property
    def hora_fim_dt(self):
        """Retorna o datetime de fim do agendamento, baseado na duração do serviço."""
        inicio = self.hora_inicio_dt
        if not inicio or not self.servico_id:
             return None
        try:
            # self.servico.duracao já é um timedelta
            return inicio + self.servico.duracao
        except Servico.DoesNotExist:
             return None
        except AttributeError: # Caso servico não tenha duracao
             return None

    def clean(self):
        """Validações personalizadas considerando a duração do serviço."""
        super().clean() # Chama validações da superclasse primeiro

        if not self.servico_id or not self.hora or not self.data or not self.profissional_id:
             # Validação básica de campos necessários para as lógicas seguintes
             # O serializer cuidará de campos obrigatórios ausentes
             return

        # --- Validação Serviço x Profissional ---
        try:
            # Verifica se o serviço existe e busca a instância
            servico_obj = Servico.objects.get(pk=self.servico_id)
            if self.profissional not in servico_obj.profissionais.all():
                 raise ValidationError(f"O serviço '{servico_obj.nome}' não é oferecido pelo profissional '{self.profissional.nome_completo}'.")
        except Servico.DoesNotExist:
             raise ValidationError("Serviço selecionado não existe.")


        # --- Cálculo dos Datetimes de Início e Fim ---
        inicio_dt = self.hora_inicio_dt
        fim_dt = self.hora_fim_dt

        if not inicio_dt or not fim_dt:
             raise ValidationError("Não foi possível determinar o início ou fim do agendamento (verifique data, hora e duração do serviço).")

        if fim_dt <= inicio_dt:
             raise ValidationError("A duração do serviço resulta em um horário de término inválido.")


        # --- Validação do Expediente ---
        dia_semana = self.data.weekday()
        try:
            expediente = HorarioExpediente.objects.prefetch_related('horarios').get(
                profissional=self.profissional,
                dia_semana=dia_semana
            )
            horarios_expediente_set = {h.horario for h in expediente.horarios.all()}
        except HorarioExpediente.DoesNotExist:
            data_formatada = self.data.strftime('%d/%m/%Y')
            raise ValidationError(f"O profissional {self.profissional} não possui expediente na data {data_formatada}.")

        # Verifica se todos os slots necessários estão DENTRO do expediente
        horario_atual_dt = inicio_dt
        while horario_atual_dt < fim_dt:
            slot_time = horario_atual_dt.time()
            if slot_time not in horarios_expediente_set:
                hora_fmt = slot_time.strftime('%H:%M')
                raise ValidationError(f"O horário {hora_fmt} (necessário devido à duração) está fora do expediente do profissional.")
            horario_atual_dt += timedelta(minutes=30) # Assume incrementos de 30 min


        # --- Validação de Conflitos (Overlap) ---
        # Encontra agendamentos existentes que *poderiam* conflitar
        agendamentos_conflitantes_qs = Agendamento.objects.filter(
            profissional=self.profissional,
            data=self.data
        ).select_related('servico') # Pega o serviço para calcular o fim

        if self.pk: # Exclui o próprio agendamento durante a edição
            agendamentos_conflitantes_qs = agendamentos_conflitantes_qs.exclude(pk=self.pk)

        # Verifica sobreposição com cada agendamento existente
        for ag_existente in agendamentos_conflitantes_qs:
            inicio_existente_dt = ag_existente.hora_inicio_dt
            fim_existente_dt = ag_existente.hora_fim_dt

            if not inicio_existente_dt or not fim_existente_dt:
                 continue # Pula agendamentos existentes inválidos

            # Condição de sobreposição: (StartA < EndB) and (EndA > StartB)
            if (inicio_dt < fim_existente_dt) and (fim_dt > inicio_existente_dt):
                hora_fmt_existente = inicio_existente_dt.strftime('%H:%M')
                raise ValidationError(
                    f"Conflito: Este horário sobrepõe um agendamento existente do profissional às {hora_fmt_existente}."
                )

        # --- Validação de Conflitos para o Cliente (similar) ---
        agendamentos_cliente_qs = Agendamento.objects.filter(
            cliente=self.cliente,
            data=self.data
        ).select_related('servico')

        if self.pk:
            agendamentos_cliente_qs = agendamentos_cliente_qs.exclude(pk=self.pk)

        for ag_cliente_existente in agendamentos_cliente_qs:
            inicio_cli_existente_dt = ag_cliente_existente.hora_inicio_dt
            fim_cli_existente_dt = ag_cliente_existente.hora_fim_dt

            if not inicio_cli_existente_dt or not fim_cli_existente_dt:
                 continue

            if (inicio_dt < fim_cli_existente_dt) and (fim_dt > inicio_cli_existente_dt):
                hora_fmt_cli_existente = inicio_cli_existente_dt.strftime('%H:%M')
                raise ValidationError(
                    f"Conflito: O cliente já possui um agendamento neste período (iniciando às {hora_fmt_cli_existente})."
                )


    def save(self, *args, **kwargs):
        """Chama clean() antes de salvar."""
        self.clean() # Garante que as validações sejam executadas
        super().save(*args, **kwargs)

    # O método estático horarios_ocupados não é mais necessário com a nova lógica de view
    # @staticmethod
    # def horarios_ocupados(profissional, data): ...

    class Meta:
        ordering = ['data', 'hora']
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
