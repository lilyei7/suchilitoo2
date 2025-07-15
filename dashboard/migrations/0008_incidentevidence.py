from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('dashboard', '0007_checklistcategory_checklisttask_incidentreport_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentEvidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='checklist/incidents/%Y/%m/%d/', verbose_name='Archivo')),
                ('comment', models.TextField(blank=True, verbose_name='Comentario')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence_files', to='dashboard.incidentreport', verbose_name='Reporte de incidente')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_incident_evidence', to='accounts.usuario', verbose_name='Subido por')),
            ],
            options={
                'verbose_name': 'Evidencia de Incidente',
                'verbose_name_plural': 'Evidencias de Incidentes',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
