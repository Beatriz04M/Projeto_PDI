# Generated by Django 4.2.20 on 2025-05-07 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Biblioteca', '0012_alter_estante_cor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estante',
            name='cor',
            field=models.CharField(blank=True, default='f9b4c6', max_length=7, null=True),
        ),
    ]
