# Generated by Django 4.2.20 on 2025-06-14 19:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Livros', '0009_alter_livro_ano_publicacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='leitura',
            name='avaliacao',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)]),
        ),
    ]
