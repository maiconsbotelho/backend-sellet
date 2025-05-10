from rest_framework import serializers
from .models import Usuario, TipoUsuario


class UsuarioSerializer(serializers.ModelSerializer):
    # Agora o campo é uma URL (string), não mais imagem binária
    foto_perfil = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nome_completo', 'tipo', 'created_at', 'updated_at',
            'telefone', 'cpf', 'cep', 'rua', 'numero_casa', 'cidade', 'uf',
            'is_active', 'foto_perfil'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'telefone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cpf': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cep': {'required': False, 'allow_null': True, 'allow_blank': True},
            'rua': {'required': False, 'allow_null': True, 'allow_blank': True},
            'numero_casa': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cidade': {'required': False, 'allow_null': True, 'allow_blank': True},
            'uf': {'required': False, 'allow_null': True, 'allow_blank': True},
        }


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    foto_perfil = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Usuario
        fields = [
            'email', 'nome_completo', 'tipo', 'password',
            'telefone', 'cpf', 'cep', 'rua', 'numero_casa', 'cidade', 'uf',
            'foto_perfil'
        ]
        extra_kwargs = {
            'telefone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cpf': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cep': {'required': False, 'allow_null': True, 'allow_blank': True},
            'rua': {'required': False, 'allow_null': True, 'allow_blank': True},
            'numero_casa': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cidade': {'required': False, 'allow_null': True, 'allow_blank': True},
            'uf': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def validate_tipo(self, value):
        if value not in [TipoUsuario.CLIENTE, TipoUsuario.PROFISSIONAL]:
            raise serializers.ValidationError("Tipo de usuário inválido para criação.")
        return value

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)
