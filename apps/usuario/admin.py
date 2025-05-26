from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, TipoUsuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    model = Usuario
    list_display = ('id', 'nome_completo', 'email', 'tipo', 'is_active', 'is_staff', 'created_at')
    list_filter = ('tipo', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'nome_completo', 'cpf', 'telefone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome_completo', 'tipo', 'telefone', 'cpf', 'foto_perfil')}),
        ('Endereço', {'fields': ('cep', 'rua', 'numero_casa', 'cidade', 'uf')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome_completo', 'tipo', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
