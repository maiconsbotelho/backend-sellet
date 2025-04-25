from django.db import models
from apps.usuario.models import Usuario
from apps.usuario.models import TipoUsuario


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    duracao = models.DurationField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    profissionais = models.ManyToManyField(
        Usuario,
        related_name='servicos',
        limit_choices_to={'tipo': TipoUsuario.PROFISSIONAL}
    )

    def __str__(self):
        return self.nome
