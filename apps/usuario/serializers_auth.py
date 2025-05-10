from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password'),
        }

        if not credentials[self.username_field] or not credentials['password']:
            raise serializers.ValidationError('Email e senha são obrigatórios.')

        user = authenticate(**credentials)

        if user is None:
            raise serializers.ValidationError('Email ou senha inválidos.')

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

