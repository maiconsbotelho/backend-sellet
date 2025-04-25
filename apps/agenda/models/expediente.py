from django.db import models
from datetime import time

DIAS_DA_SEMANA = [
    (0, 'Segunda'),
    (1, 'Terça'),
    (2, 'Quarta'),
    (3, 'Quinta'),
    (4, 'Sexta'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]

HORARIOS_DISPONIVEIS = [
    (0, '08:00'),
    (1, '08:30'),
    (2, '09:00'),
    (3, '09:30'),
    (4, '10:00'),
    (5, '10:30'),
    (6, '11:00'),
    (7, '11:30'),
    (8, '12:00'),
    (9, '12:30'),
    (10, '13:00'),
    (11, '13:30'),
    (12, '14:00'),
    (13, '14:30'),
    (14, '15:00'),
    (15, '15:30'),
    (16, '16:00'),
    (17, '16:30'),
    (18, '17:00'),
    (19, '17:30'),
    (20, '18:00'),
    (21, '18:30'),
    (22, '19:00'),
    (23, '19:30'),
    (24, '20:00'),
]

class HorarioExpediente(models.Model):
    profissional = models.ForeignKey(
        'usuario.Usuario',
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'PROFISSIONAL'}
    )
    dia_semana = models.IntegerField(choices=DIAS_DA_SEMANA)
    horarios = models.ManyToManyField('Horario', related_name='expedientes')

    def __str__(self):
        return f"{self.profissional} - {DIAS_DA_SEMANA[self.dia_semana][1]}"

class Horario(models.Model):
    horario = models.TimeField()

    def __str__(self):
        return self.horario.strftime('%H:%M')