from rest_framework import serializers
from apps.agenda.models import Agendamento

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'

    def validate(self, data):
        if self.instance:
            # É uma edição: use a instância existente e atualize os dados nela
            for attr, value in data.items():
                setattr(self.instance, attr, value)
            self.instance.clean()
        else:
            # É uma criação: instancia novo agendamento
            agendamento = Agendamento(**data)
            agendamento.clean()
        return data
