from rest_framework import serializers
# Remova make_password se não for mais usado em outro lugar neste arquivo
# from django.contrib.auth.hashers import make_password
from .models import Usuario, TipoUsuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nome_completo', 'tipo', 'created_at', 'updated_at',
            'telefone', 'cpf', 'cep', 'rua', 'numero_casa', 'cidade', 'uf',
            'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'telefone': {'required': False, 'allow_null': True},
            'cpf': {'required': False, 'allow_null': True},
            'cep': {'required': False, 'allow_null': True},
            'rua': {'required': False, 'allow_null': True},
            'numero_casa': {'required': False, 'allow_null': True},
            'cidade': {'required': False, 'allow_null': True},
            'uf': {'required': False, 'allow_null': True},
        }

class UsuarioCreateSerializer(serializers.ModelSerializer):
    # Mantenha password como write_only e required para validação da entrada
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Usuario
        fields = [
            'email', 'nome_completo', 'tipo', 'password', # password necessário para validação
            'telefone', 'cpf', 'cep', 'rua', 'numero_casa', 'cidade', 'uf'
        ]
        extra_kwargs = {
            # password não precisa de extra_kwargs se definido explicitamente acima
            'telefone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cpf': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cep': {'required': False, 'allow_null': True, 'allow_blank': True},
            'rua': {'required': False, 'allow_null': True, 'allow_blank': True},
            'numero_casa': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cidade': {'required': False, 'allow_null': True, 'allow_blank': True},
            'uf': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def validate_tipo(self, value):
        # Permite apenas CLIENTE ou PROFISSIONAL para criação via este serializer
        if value not in [TipoUsuario.CLIENTE, TipoUsuario.PROFISSIONAL]:
            raise serializers.ValidationError("Tipo de usuário inválido para criação.")
        return value

    def create(self, validated_data):
        # Use o método create_user do gerenciador personalizado.
        # Ele lida com o hash da senha internamente via set_password.
        # Todos os campos em validated_data (incluindo os opcionais se presentes)
        # serão passados como kwargs para create_user.
        user = Usuario.objects.create_user(**validated_data)
        return user
