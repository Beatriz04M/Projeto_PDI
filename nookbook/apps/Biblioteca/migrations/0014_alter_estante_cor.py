# Generated by Django 4.2.20 on 2025-05-07 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Biblioteca', '0013_alter_estante_cor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estante',
            name='cor',
            field=models.CharField(blank=True, default='#f5f5f5', max_length=7, null=True),
        ),
    ]
