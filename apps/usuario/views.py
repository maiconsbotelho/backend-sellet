from rest_framework import viewsets
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    API para gerenciar usuários:
    - Listar, criar, editar e deletar usuários.
    - Filtrar usuários por tipo (?tipo=CLIENTE, PROFISSIONAL, ADMIN).
    """
    queryset = Usuario.objects.all()

    def get_queryset(self):
        """
        Permite filtrar usuários por tipo usando o parâmetro ?tipo=
        Exemplo: /api/usuarios/?tipo=CLIENTE
        """
        tipo = self.request.query_params.get('tipo')
        if tipo:
            return self.queryset.filter(tipo=tipo)
        return self.queryset

    def get_serializer_class(self):
        """
        Usa o serializer de criação para POST, e o padrão para outras ações.
        """
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        """
        Salva um novo usuário.
        """
        serializer.save()
