from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/servicos/', include('apps.servicos.urls')),
    path('api/usuario/', include('apps.usuario.urls')),
    path('api/agenda/', include('apps.agenda.urls')),
]

# Serve arquivos de mídia apenas no modo DEBUG (desenvolvimento)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
