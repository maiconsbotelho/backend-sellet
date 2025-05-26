from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta

from apps.usuario.models import Usuario, TipoUsuario


class Servico(models.Model):
    """
    Modelo para representar os serviços oferecidos pela Esmalteria.
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    duracao = models.DurationField(
        default=timedelta(minutes=30),
        help_text="Duração do serviço (ex: 0:30:00 para 30 min, 1:30:00 para 1h30)."
    )
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Preço do serviço (em reais)."
    )

    profissionais = models.ManyToManyField(
        Usuario,
        related_name='servicos',
        limit_choices_to={'tipo': TipoUsuario.PROFISSIONAL},
        help_text="Profissionais habilitados para realizar este serviço."
    )

    def __str__(self):
        return self.nome

    def clean(self):
        """
        Validações adicionais para o serviço:
        - A duração deve ser positiva.
        - A duração deve ser múltiplo de 30 minutos (opcional, apenas aviso).
        """
        super().clean()

        if self.duracao <= timedelta(0):
            raise ValidationError("A duração do serviço deve ser positiva.")

        if self.duracao.total_seconds() % (30 * 60) != 0:
            print(f"Aviso: Serviço '{self.nome}' tem duração ({self.duracao}) que não é múltiplo exato de 30 minutos.")
