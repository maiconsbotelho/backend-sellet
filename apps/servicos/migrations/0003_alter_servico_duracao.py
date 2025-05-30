# Generated by Django 5.1.7 on 2025-05-05 22:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servico',
            name='duracao',
            field=models.DurationField(default=datetime.timedelta(seconds=1800), help_text='Duração do serviço (ex: 0:30:00 para 30 min, 1:30:00 para 1h30)'),
        ),
    ]
