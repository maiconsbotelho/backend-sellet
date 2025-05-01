from rest_framework import serializers
from apps.agenda.models import HorarioExpediente, Horario
from datetime import datetime, timedelta, time # Adicionado time

class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = ['id', 'horario']

class HorarioExpedienteSerializer(serializers.ModelSerializer):
    # read_only=True significa que 'horarios' será incluído na resposta GET,
    # mas não será esperado diretamente no payload de escrita (POST/PUT).
    horarios = HorarioSerializer(many=True, read_only=True)
    # write_only=True significa que 'inicio' e 'fim' são esperados no payload
    # de escrita (POST/PUT), mas não serão incluídos na resposta GET por padrão.
    inicio = serializers.TimeField(write_only=True, format='%H:%M') # Especificar formato pode ajudar
    fim = serializers.TimeField(write_only=True, format='%H:%M')    # Especificar formato pode ajudar

    class Meta:
        model = HorarioExpediente
        # Inclui os campos do modelo e os campos write_only para escrita
        fields = ['id', 'profissional', 'dia_semana', 'horarios', 'inicio', 'fim']
        # 'horarios' é efetivamente read-only aqui por causa do HorarioSerializer aninhado
        # mas 'inicio' e 'fim' são write-only.

    def _gerar_e_associar_horarios(self, instance, inicio, fim):
        """Lógica auxiliar para gerar e associar horários."""
        # Limpa os horários antigos associados a esta instância
        instance.horarios.clear()

        # Gera e associa os novos horários
        try:
            # Tenta combinar com uma data qualquer para permitir a adição de timedelta
            horario_atual_dt = datetime.combine(datetime.today(), inicio)
            fim_dt = datetime.combine(datetime.today(), fim)

            while horario_atual_dt <= fim_dt:
                horario_time = horario_atual_dt.time()
                # Garante que o objeto Horario exista no banco ou o cria
                horario_obj, created = Horario.objects.get_or_create(horario=horario_time)
                # Adiciona a associação ManyToMany
                instance.horarios.add(horario_obj)
                # Incrementa 30 minutos
                horario_atual_dt += timedelta(minutes=30)
        except Exception as e:
            # Logar o erro pode ser útil
            print(f"Erro ao gerar horários: {e}")
            # Você pode querer levantar uma serializers.ValidationError aqui
            raise serializers.ValidationError("Erro ao processar os horários de início e fim.")


    def create(self, validated_data):
        # Remove 'inicio' e 'fim' pois não são campos diretos do modelo HorarioExpediente
        inicio = validated_data.pop('inicio')
        fim = validated_data.pop('fim')

        # Cria a instância de HorarioExpediente com os campos restantes
        expediente = HorarioExpediente.objects.create(**validated_data)

        # Usa a lógica auxiliar para gerar e associar os horários
        self._gerar_e_associar_horarios(expediente, inicio, fim)

        return expediente

    def update(self, instance, validated_data):
        # Remove 'inicio' e 'fim' se presentes, pois serão tratados separadamente
        inicio = validated_data.pop('inicio', None)
        fim = validated_data.pop('fim', None)

        # Atualiza os campos padrão do modelo (profissional, dia_semana), se fornecidos.
        # É importante notar que geralmente não se altera profissional ou dia_semana
        # ao editar apenas os horários, mas o DRF permite isso por padrão no PUT.
        instance.profissional = validated_data.get('profissional', instance.profissional)
        instance.dia_semana = validated_data.get('dia_semana', instance.dia_semana)
        instance.save() # Salva as alterações nos campos diretos, se houver

        # Se 'inicio' e 'fim' foram fornecidos na requisição PUT,
        # atualiza os horários associados.
        if inicio is not None and fim is not None:
             # Usa a lógica auxiliar para limpar os antigos e gerar/associar os novos
            self._gerar_e_associar_horarios(instance, inicio, fim)
        elif inicio is not None or fim is not None:
             # Se apenas um foi fornecido, isso pode ser um erro ou lógica não suportada
             raise serializers.ValidationError("Para atualizar os horários, forneça 'inicio' e 'fim'.")

        # Retorna a instância atualizada. O DRF cuidará de serializá-la
        # corretamente para a resposta (incluindo os 'horarios' atualizados
        # porque 'horarios' é read_only=True no serializer aninhado).
        return instance
