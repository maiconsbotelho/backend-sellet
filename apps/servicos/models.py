from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta # Import timedelta
from apps.usuario.models import Usuario
from apps.usuario.models import TipoUsuario


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    # DurationField armazena um timedelta (dias, segundos, microssegundos)
    duracao = models.DurationField(default=timedelta(minutes=30), help_text="Duração do serviço (ex: 0:30:00 para 30 min, 1:30:00 para 1h30)")
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    profissionais = models.ManyToManyField(
        Usuario,
        related_name='servicos',
        limit_choices_to={'tipo': TipoUsuario.PROFISSIONAL}
    )

    def __str__(self):
        return self.nome

    def clean(self):
        """Validações adicionais para o serviço."""
        super().clean()
        # Validação opcional: Verificar se a duração é múltiplo de 30 minutos
        if self.duracao.total_seconds() % (30 * 60) != 0:
            # Você pode levantar um ValidationError ou apenas logar um aviso
            # raise ValidationError("A duração do serviço deve ser um múltiplo de 30 minutos.")
            print(f"Aviso: Serviço '{self.nome}' tem duração ({self.duracao}) que não é múltiplo exato de 30 minutos.")
        if self.duracao <= timedelta(0):
             raise ValidationError("A duração do serviço deve ser positiva.")

    # Não é necessário save() aqui, a validação é chamada automaticamente pelo ModelForm/Admin ou manualmente.
