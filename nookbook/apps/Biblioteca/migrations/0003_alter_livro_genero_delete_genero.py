# Generated by Django 4.2.20 on 2025-03-27 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Biblioteca', '0002_genero_generos_alter_avaliacao_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livro',
            name='genero',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='livros', to='Biblioteca.generos'),
        ),
        migrations.DeleteModel(
            name='Genero',
        ),
    ]
