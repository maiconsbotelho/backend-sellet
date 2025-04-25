from rest_framework import serializers
from apps.agenda.models import HorarioExpediente, Horario
from datetime import datetime, timedelta

class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = ['id', 'horario']

class HorarioExpedienteSerializer(serializers.ModelSerializer):
    horarios = HorarioSerializer(many=True, read_only=True)
    inicio = serializers.TimeField(write_only=True)
    fim = serializers.TimeField(write_only=True)

    class Meta:
        model = HorarioExpediente
        fields = ['id', 'profissional', 'dia_semana', 'horarios', 'inicio', 'fim']

    def create(self, validated_data):
        inicio = validated_data.pop('inicio')
        fim = validated_data.pop('fim')
        expediente = HorarioExpediente.objects.create(**validated_data)

        # Gerar horários de 30 em 30 minutos
        horario_atual = datetime.combine(datetime.today(), inicio)
        fim_datetime = datetime.combine(datetime.today(), fim)
        while horario_atual <= fim_datetime:
            horario, created = Horario.objects.get_or_create(horario=horario_atual.time())
            expediente.horarios.add(horario)
            horario_atual += timedelta(minutes=30)

        return expediente