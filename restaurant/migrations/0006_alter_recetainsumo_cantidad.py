# Generated by Django 5.2.4 on 2025-07-16 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0005_configuracionsistema'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recetainsumo',
            name='cantidad',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
    ]
