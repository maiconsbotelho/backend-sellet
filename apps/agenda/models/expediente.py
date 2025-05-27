from django.db import models

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
    (0, '06:00'),
    (1, '06:30'),
    (2, '07:00'),
    (3, '07:30'),
    (4, '08:00'),
    (5, '08:30'),
    (6, '09:00'),
    (7, '09:30'),
    (8, '10:00'),
    (9, '10:30'),
    (10, '11:00'),
    (11, '11:30'),
    (12, '12:00'),
    (13, '12:30'),
    (14, '13:00'),
    (15, '13:30'),
    (16, '14:00'),
    (17, '14:30'),
    (18, '15:00'),
    (19, '15:30'),
    (20, '16:00'),
    (21, '16:30'),
    (22, '17:00'),
    (23, '17:30'),
    (24, '18:00'),
    (25, '18:30'),
    (26, '19:00'),
    (27, '19:30'),
    (28, '20:00'),
    (29, '20:30'),
    (30, '21:00'),
    (31, '21:30'),
    (32, '22:00'),
    (33, '22:30'),
    (34, '23:00'),
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
        return f"{self.profissional} - {dict(DIAS_DA_SEMANA).get(self.dia_semana, 'Desconhecido')}"


class Horario(models.Model):
    horario = models.TimeField()

    def __str__(self):
        return self.horario.strftime('%H:%M')
