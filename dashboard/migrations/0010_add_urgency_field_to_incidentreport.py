from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentreport',
            name='urgency',
            field=models.CharField(choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('critica', 'Crítica')], default='media', max_length=10, verbose_name='Nivel de Urgencia'),
        ),
    ]
