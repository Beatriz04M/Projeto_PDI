# Generated by Django 4.2.20 on 2025-06-15 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Livros', '0013_alter_livro_ano_publicacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='avaliacao',
            name='data',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
