from django.db import models
from django.core.exceptions import ValidationError
from datetime import time

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
        return f"{self.data} às {self.hora} - {self.cliente} com {self.profissional}"

    def clean(self):
        """Validações personalizadas."""
        from apps.agenda.models.expediente import HorarioExpediente

        # Obtém o dia da semana da data do agendamento (0 = Segunda, 6 = Domingo).
        dia_semana = self.data.weekday()

        # Verifica se o profissional tem expediente no dia da semana.
        try:
            expediente = HorarioExpediente.objects.get(
                profissional=self.profissional,
                dia_semana=dia_semana
            )
        except HorarioExpediente.DoesNotExist:
            raise ValidationError(f"O profissional {self.profissional} não possui expediente na data {self.data}.")

        # Verifica se o horário do agendamento está dentro do expediente.
        if not expediente.horarios.filter(horario=self.hora).exists():
            raise ValidationError(f"O horário {self.hora} não está disponível no expediente do profissional {self.profissional}.")

        # Verifica se já existe um agendamento para o mesmo profissional no mesmo dia e horário.
        if Agendamento.objects.filter(
            profissional=self.profissional,
            data=self.data,
            hora=self.hora
        ).exists():
            raise ValidationError(f"O profissional {self.profissional} já possui um agendamento no horário {self.hora}.")

        # Verifica se o cliente já possui um agendamento no mesmo horário.
        if Agendamento.objects.filter(
            cliente=self.cliente,
            data=self.data,
            hora=self.hora
        ).exists():
            raise ValidationError(f"O cliente {self.cliente} já possui um agendamento no horário {self.hora}.")
        
    @staticmethod
    def horarios_ocupados(profissional, data):
        """Retorna os horários ocupados de um profissional em uma data específica."""
        return Agendamento.objects.filter(
            profissional=profissional,
            data=data
        ).values_list('hora', flat=True)

    class Meta:
        # Define a ordenação padrão dos registros: primeiro pela data, depois pela hora.
        ordering = ['data', 'hora']
        # Nome amigável para o modelo no singular (usado no admin do Django).
        verbose_name = "Agendamento"
        # Nome amigável para o modelo no plural (usado no admin do Django).
        verbose_name_plural = "Agendamentos"