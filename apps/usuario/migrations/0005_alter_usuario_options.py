# Generated by Django 5.2 on 2025-05-10 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0004_alter_usuario_foto_perfil'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usuario',
            options={'verbose_name': 'Usuário', 'verbose_name_plural': 'Usuários'},
        ),
    ]
