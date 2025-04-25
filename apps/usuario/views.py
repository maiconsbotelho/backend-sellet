from rest_framework import viewsets
from .models import Usuario, TipoUsuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()

    def get_queryset(self):
        # Filtra dinamicamente com base no parâmetro 'tipo'
        tipo = self.request.query_params.get('tipo')
        if tipo:
            # Retorna apenas os usuários do tipo especificado
            return self.queryset.filter(tipo=tipo)
        # Retorna todos os usuários, incluindo CLIENTE, PROFISSIONAL e ADMIN
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        serializer.save()