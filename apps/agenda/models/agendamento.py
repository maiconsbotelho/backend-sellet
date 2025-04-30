from django.db import models
from django.core.exceptions import ValidationError
from datetime import time, datetime, timedelta # Added timedelta
from apps.agenda.models.expediente import Horario, HorarioExpediente
from rest_framework.decorators import action
from rest_framework.response import Response
# Import Usuario model if not already implicitly available via ForeignKey string
# from apps.usuario.models import Usuario
# Import Servico model if not already implicitly available via ForeignKey string
# from apps.servicos.models import Servico

class Agendamento(models.Model):
    # Relacionamento com o modelo Cliente. Um agendamento pertence a um cliente.
    cliente = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, limit_choices_to={'tipo': 'CLIENTE'}, related_name='agendamentos_como_cliente' )
    # Relacionamento com o modelo Profissional. Um agendamento pertence a um profissional.
    profissional = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, limit_choices_to={'tipo': 'PROFISSIONAL'}, related_name='agendamentos_como_profissional')
    # Relacionamento com o modelo Servico. Um agendamento está associado a um serviço específico.
    servico = models.ForeignKey('servicos.Servico', on_delete=models.CASCADE)
    # Campo para armazenar a data do agendamento.
    data = models.DateField()
    # Campo para armazenar a hora do agendamento.
    hora = models.TimeField()

    def __str__(self):
        # Retorna uma string no formato "data às hora - cliente com profissional".
        # Format time for better readability
        hora_formatada = self.hora.strftime('%H:%M')
        return f"{self.data} às {hora_formatada} - {self.cliente} com {self.profissional}"

    def clean(self):
        """Validações personalizadas."""
        # No need to import HorarioExpediente again if already imported at top level

        # Obtém o dia da semana da data do agendamento (0 = Segunda, 6 = Domingo).
        dia_semana = self.data.weekday()

        # Verifica se o profissional tem expediente no dia da semana.
        try:
            expediente = HorarioExpediente.objects.get(
                profissional=self.profissional,
                dia_semana=dia_semana
            )
        except HorarioExpediente.DoesNotExist:
            # Format date for the error message
            data_formatada = self.data.strftime('%d/%m/%Y')
            raise ValidationError(f"O profissional {self.profissional} não possui expediente na data {data_formatada}.")

        # Verifica se o horário do agendamento está dentro do expediente.
        if not expediente.horarios.filter(horario=self.hora).exists():
            hora_formatada = self.hora.strftime('%H:%M')
            raise ValidationError(f"O horário {hora_formatada} não está disponível no expediente do profissional {self.profissional}.")

        # Verifica se já existe um agendamento para o mesmo profissional no mesmo dia e horário.
        # Exclude self if instance already exists (for updates)
        qs = Agendamento.objects.filter(
            profissional=self.profissional,
            data=self.data,
            hora=self.hora
        )
        if self.pk: # If instance has a primary key, it's an update
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            hora_formatada = self.hora.strftime('%H:%M')
            raise ValidationError(f"O profissional {self.profissional} já possui um agendamento no horário {hora_formatada}.")

        # Verifica se o cliente já possui um agendamento no mesmo horário.
        # Exclude self if instance already exists (for updates)
        qs_cliente = Agendamento.objects.filter(
            cliente=self.cliente,
            data=self.data,
            hora=self.hora
        )
        if self.pk: # If instance has a primary key, it's an update
            qs_cliente = qs_cliente.exclude(pk=self.pk)
        if qs_cliente.exists():
            hora_formatada = self.hora.strftime('%H:%M')
            raise ValidationError(f"O cliente {self.cliente} já possui um agendamento no horário {hora_formatada}.")

        # Verifica se o serviço selecionado é oferecido pelo profissional
        if self.profissional not in self.servico.profissionais.all():
             raise ValidationError(f"O serviço '{self.servico.nome}' não é oferecido pelo profissional '{self.profissional.nome_completo}'.")


    def save(self, *args, **kwargs):
        """Chama clean() antes de salvar."""
        self.clean()
        super().save(*args, **kwargs)

    @staticmethod
    def horarios_ocupados(profissional, data):
        """Retorna os horários ocupados de um profissional em uma data específica."""
        return Agendamento.objects.filter(
            profissional=profissional,
            data=data
        ).values_list('hora', flat=True)

    # Note: The @action 'agenda' is part of the ViewSet (AgendamentoViewSet), not the model.
    # It was previously shown in the context but belongs in views/agendamento.py.
    # Keeping the Meta class here as it belongs to the model.

    class Meta:
        # Define a ordenação padrão dos registros: primeiro pela data, depois pela hora.
        ordering = ['data', 'hora']
        # Nome amigável para o modelo no singular (usado no admin do Django).
        verbose_name = "Agendamento"
        # Nome amigável para o modelo no plural (usado no admin do Django).
        verbose_name_plural = "Agendamentos"