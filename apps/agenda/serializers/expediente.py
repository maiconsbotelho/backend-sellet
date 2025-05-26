from rest_framework import serializers
from datetime import datetime, timedelta

from apps.agenda.models import HorarioExpediente, Horario


class HorarioSerializer(serializers.ModelSerializer):
    horario = serializers.TimeField(format='%H:%M')  # Adiciona o formato
    
    class Meta:
        model = Horario
        fields = ['id', 'horario']


class HorarioExpedienteSerializer(serializers.ModelSerializer):
    horarios = HorarioSerializer(many=True, read_only=True)
    inicio = serializers.TimeField(write_only=True, format='%H:%M')
    fim = serializers.TimeField(write_only=True, format='%H:%M')

    class Meta:
        model = HorarioExpediente
        fields = ['id', 'profissional', 'dia_semana', 'horarios', 'inicio', 'fim']

    def _gerar_e_associar_horarios(self, instance, inicio, fim):
        """
        Gera e associa horários ao expediente em blocos de 30 minutos.
        """
        instance.horarios.clear()

        try:
            atual_dt = datetime.combine(datetime.today(), inicio)
            fim_dt = datetime.combine(datetime.today(), fim)

            while atual_dt <= fim_dt:
                horario_time = atual_dt.time()
                horario_obj, _ = Horario.objects.get_or_create(horario=horario_time)
                instance.horarios.add(horario_obj)
                atual_dt += timedelta(minutes=30)

        except Exception as e:
            print(f"Erro ao gerar horários: {e}")
            raise serializers.ValidationError("Erro ao processar os horários de início e fim.")

    def create(self, validated_data):
        inicio = validated_data.pop('inicio')
        fim = validated_data.pop('fim')

        expediente = HorarioExpediente.objects.create(**validated_data)
        self._gerar_e_associar_horarios(expediente, inicio, fim)

        return expediente

    def update(self, instance, validated_data):
        inicio = validated_data.pop('inicio', None)
        fim = validated_data.pop('fim', None)

        instance.profissional = validated_data.get('profissional', instance.profissional)
        instance.dia_semana = validated_data.get('dia_semana', instance.dia_semana)
        instance.save()

        if inicio is not None and fim is not None:
            self._gerar_e_associar_horarios(instance, inicio, fim)
        elif inicio is not None or fim is not None:
            raise serializers.ValidationError("Para atualizar os horários, forneça 'inicio' e 'fim'.")

        return instance
    

    def validate(self, data):
        inicio = data.get("inicio")
        fim = data.get("fim")

        if inicio and fim and inicio >= fim:
            raise serializers.ValidationError("O horário de início deve ser menor que o horário de fim.")

        return data

