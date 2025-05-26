from rest_framework import serializers
from apps.agenda.models import Agendamento

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'

    def validate(self, data):
        """
        Chama o método clean() do model para validar as regras de negócio.
        Garante que as mesmas validações do model sejam aplicadas no serializer.
        """
        # Validação de edição (update)
        if self.instance:
            for attr, value in data.items():
                setattr(self.instance, attr, value)
            self.instance.clean()
        else:
            # Validação de criação (create)
            agendamento = Agendamento(**data)
            agendamento.clean()

        return data
