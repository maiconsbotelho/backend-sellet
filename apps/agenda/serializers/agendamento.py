from rest_framework import serializers
from apps.agenda.models import Agendamento

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'

    def validate(self, data):
        """
        Validações adicionais no serializer.
        """
        agendamento = Agendamento(**data)
        agendamento.clean()  # Chama o método clean do modelo para validações personalizadas
        return data