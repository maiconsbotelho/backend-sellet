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

        user = self.context['request'].user
        print(f"DEBUG: user={user}, tipo={getattr(user, 'tipo', None)}")
        tipos_livres = ['PROFISSIONAL', 'ADMIN']
        if hasattr(user, 'tipo') and user.tipo in tipos_livres:
        # Se o usuário autenticado for profissional ou admin, permite agendamento livre,
        # pulando as validações de conflito de horário e expediente.
            return data
        
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
