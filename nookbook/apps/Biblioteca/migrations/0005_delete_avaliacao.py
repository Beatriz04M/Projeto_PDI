# Generated by Django 4.2.20 on 2025-04-24 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Biblioteca', '0004_recomendacao_remove_livro_genero_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Avaliacao',
        ),
    ]
