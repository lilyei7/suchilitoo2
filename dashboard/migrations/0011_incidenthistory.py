# Generated manually to fix migration issues

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_incidentevidence'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('creado', 'Creado'), ('cambio_estado', 'Cambio de Estado'), ('reasignado', 'Reasignado'), ('cerrado', 'Cerrado'), ('evidencia_agregada', 'Evidencia Agregada'), ('comentario', 'Comentario')], max_length=20)),
                ('description', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incident_actions', to='dashboard.usuario')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='dashboard.incidentreport')),
            ],
        ),
    ]