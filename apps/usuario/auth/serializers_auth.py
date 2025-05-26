from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para login com email e senha.
    Retorna access_token e refresh_token em caso de sucesso.
    """
    username_field = 'email'

    def validate(self, attrs):
        # Captura as credenciais do request
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password'),
        }

        # Verifica campos obrigatórios
        if not credentials[self.username_field] or not credentials['password']:
            raise serializers.ValidationError('Email e senha são obrigatórios.')

        # Autentica o usuário
        user = authenticate(**credentials)
        if user is None:
            raise serializers.ValidationError('Email ou senha inválidos.')

        # Gera os tokens JWT
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
