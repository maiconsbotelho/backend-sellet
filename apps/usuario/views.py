from rest_framework import viewsets
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, editar e deletar usuários.
    """
    queryset = Usuario.objects.all()

    def get_queryset(self):
        """
        Permite filtrar usuários por tipo (?tipo=CLIENTE, PROFISSIONAL, ADMIN)
        """
        tipo = self.request.query_params.get('tipo')
        if tipo:
            return self.queryset.filter(tipo=tipo)
        return self.queryset

    def get_serializer_class(self):
        """
        Usa serializer específico ao criar usuários (com validação de senha).
        """
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        """
        Salva um novo usuário utilizando o serializer apropriado.
        """
        serializer.save()
