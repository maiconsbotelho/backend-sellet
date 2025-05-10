from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Usuario, TipoUsuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    parser_classes = [MultiPartParser, FormParser]  # Permite upload de imagem via multipart/form-data

    def get_queryset(self):
        tipo = self.request.query_params.get('tipo')
        if tipo:
            return self.queryset.filter(tipo=tipo)
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        serializer.save()
