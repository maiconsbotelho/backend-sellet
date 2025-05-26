from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from apps.agenda.models.expediente import HorarioExpediente
from apps.servicos.models import Servico


class Agendamento(models.Model):
    cliente = models.ForeignKey(
        'usuario.Usuario',
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'CLIENTE'},
        related_name='agendamentos_como_cliente'
    )
    profissional = models.ForeignKey(
        'usuario.Usuario',
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'PROFISSIONAL'},
        related_name='agendamentos_como_profissional'
    )
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()

    class Meta:
        ordering = ['data', 'hora']
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"

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
            return inicio + self.servico.duracao
        except (Servico.DoesNotExist, AttributeError):
            return None

    def clean(self):
        """Validações personalizadas para o agendamento."""
        super().clean()

        if not self.servico_id or not self.hora or not self.data or not self.profissional_id:
            return  # Validação básica, o serializer cuida dos campos obrigatórios

        inicio_dt = self.hora_inicio_dt
        fim_dt = self.hora_fim_dt

        if not inicio_dt or not fim_dt:
            raise ValidationError("Não foi possível determinar o início ou fim do agendamento (verifique data, hora e duração do serviço).")

        if fim_dt <= inicio_dt:
            raise ValidationError("A duração do serviço resulta em um horário de término inválido.")

        # Validação: O profissional oferece o serviço?
        servico_obj = Servico.objects.filter(pk=self.servico_id).first()
        if not servico_obj:
            raise ValidationError("Serviço selecionado não existe.")
        if self.profissional not in servico_obj.profissionais.all():
            raise ValidationError(f"O serviço '{servico_obj.nome}' não é oferecido pelo profissional '{self.profissional.nome_completo}'.")

        # Validação: O horário está dentro do expediente do profissional?
        dia_semana = self.data.weekday()
        try:
            expediente = HorarioExpediente.objects.prefetch_related('horarios').get(
                profissional=self.profissional,
                dia_semana=dia_semana
            )
            horarios_expediente_set = {h.horario for h in expediente.horarios.all()}
        except HorarioExpediente.DoesNotExist:
            raise ValidationError(f"O profissional {self.profissional} não possui expediente na data {self.data.strftime('%d/%m/%Y')}.")

        horario_atual_dt = inicio_dt
        while horario_atual_dt < fim_dt:
            slot_time = horario_atual_dt.time()
            if slot_time not in horarios_expediente_set:
                hora_fmt = slot_time.strftime('%H:%M')
                raise ValidationError(f"O horário {hora_fmt} (necessário devido à duração) está fora do expediente do profissional.")
            horario_atual_dt += timedelta(minutes=30)  # Incremento de 30 minutos

        # Validação: Conflito com outros agendamentos do profissional
        agendamentos_conflitantes_qs = Agendamento.objects.filter(
            profissional=self.profissional,
            data=self.data
        ).exclude(pk=self.pk).select_related('servico')

        for ag in agendamentos_conflitantes_qs:
            if (inicio_dt < ag.hora_fim_dt) and (fim_dt > ag.hora_inicio_dt):
                hora_fmt = ag.hora_inicio_dt.strftime('%H:%M')
                raise ValidationError(f"Conflito: Este horário sobrepõe um agendamento existente do profissional às {hora_fmt}.")

        # Validação: Conflito com outros agendamentos do cliente
        agendamentos_cliente_qs = Agendamento.objects.filter(
            cliente=self.cliente,
            data=self.data
        ).exclude(pk=self.pk).select_related('servico')

        for ag in agendamentos_cliente_qs:
            if (inicio_dt < ag.hora_fim_dt) and (fim_dt > ag.hora_inicio_dt):
                hora_fmt = ag.hora_inicio_dt.strftime('%H:%M')
                raise ValidationError(f"Conflito: O cliente já possui um agendamento neste período (iniciando às {hora_fmt}).")

    def save(self, *args, **kwargs):
        """Chama clean() antes de salvar."""
        self.clean()
        super().save(*args, **kwargs)
