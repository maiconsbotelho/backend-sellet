from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now

# Define os tipos de usuários disponíveis no sistema
class TipoUsuario(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'  # Tipo de usuário administrador
    CLIENTE = 'CLIENTE', 'Cliente'    # Tipo de usuário cliente
    PROFISSIONAL = 'PROFISSIONAL', 'Profissional'  # Tipo de usuário profissional

# Gerenciador personalizado para o modelo de usuário
class UsuarioManager(BaseUserManager):
    use_in_migrations = True  # Permite que o gerenciador seja usado em migrações

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo email é obrigatório")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)  # Usuários são ativos por padrão
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('nome_completo', 'Administrador')
        extra_fields.setdefault('tipo', TipoUsuario.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('tipo') != TipoUsuario.ADMIN:
            raise ValueError('O superusuário deve ter tipo ADMIN')
        if not extra_fields.get('is_staff'):
            raise ValueError('O superusuário deve ter is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('O superusuário deve ter is_superuser=True')

        return self.create_user(email, password, **extra_fields)

# Modelo de usuário personalizado
class Usuario(AbstractUser):
    username = None  # Remove o campo username padrão do Django
    email = models.EmailField(unique=True)  # Define o e-mail como campo único e obrigatório
    nome_completo = models.CharField(max_length=255)  # Nome completo do usuário
    tipo = models.CharField(max_length=20, choices=TipoUsuario.choices)  # Tipo de usuário
    created_at = models.DateTimeField(default=now, editable=False)  # Data de criação
    updated_at = models.DateTimeField(auto_now=True)  # Data de última atualização

        # Campos opcionais adicionados
    telefone = models.CharField(max_length=15, null=True, blank=True) # Ex: 5551997562936
    cpf = models.CharField(max_length=11, null=True, blank=True, unique=True) # Ex: 07777788888 (Considerar validação e máscara)
    cep = models.CharField(max_length=8, null=True, blank=True) # Ex: 93285474 (Considerar validação)
    rua = models.CharField(max_length=255, null=True, blank=True)
    numero_casa = models.CharField(max_length=10, null=True, blank=True) # Usar CharField para flexibilidade (ex: "123A", "S/N")
    cidade = models.CharField(max_length=100, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True) # Sigla do estado (ex: RS, SP)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)


    USERNAME_FIELD = 'email'  # Define o e-mail como identificador principal para login
    REQUIRED_FIELDS = ['nome_completo', 'tipo']  # Campos obrigatórios além do e-mail

    objects = UsuarioManager()  # Usa o gerenciador personalizado para o modelo

    def __str__(self):
        return f'{self.nome_completo}'
    # return f'{self.nome_completo} ({self.get_tipo_display()})'
    

class Meta:
    verbose_name = "Usuário"
    verbose_name_plural = "Usuários"
