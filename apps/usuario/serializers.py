from rest_framework import serializers
from .models import Usuario, TipoUsuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nome_completo', 'tipo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UsuarioCreateSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Usuario
        fields = ['email', 'nome_completo', 'tipo', 'password']

    def validate_tipo(self, value):
        if value not in [TipoUsuario.CLIENTE, TipoUsuario.PROFISSIONAL]:
            raise serializers.ValidationError("Tipo de usuário inválido.")
        return value

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)