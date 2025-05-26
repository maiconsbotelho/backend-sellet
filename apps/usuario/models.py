from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now

# Tipos de usuário disponíveis
class TipoUsuario(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    CLIENTE = 'CLIENTE', 'Cliente'
    PROFISSIONAL = 'PROFISSIONAL', 'Profissional'

# Gerenciador customizado
class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo email é obrigatório")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
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

# Modelo de usuário principal
class Usuario(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TipoUsuario.choices)

    telefone = models.CharField(max_length=15, null=True, blank=True)
    cpf = models.CharField(max_length=11, null=True, blank=True, unique=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    rua = models.CharField(max_length=255, null=True, blank=True)
    numero_casa = models.CharField(max_length=10, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)

    foto_perfil = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome_completo', 'tipo']

    objects = UsuarioManager()

    def __str__(self):
        return self.nome_completo

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
