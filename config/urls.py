from django.contrib import admin
from django.urls import path, include  # Adicione o include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/servicos/', include('apps.servicos.urls')),
    path('api/usuario/', include('apps.usuario.urls')),  # Corrija o caminho para o app
    path('api/agenda/', include('apps.agenda.urls')),  # Inclua as URLs do app agenda
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)