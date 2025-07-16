# Generated manually to fix migration issues

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_remove_has_evidence_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentEvidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='incident_evidence/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('incident_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence', to='dashboard.incidentreport')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_evidence', to='dashboard.usuario')),
            ],
        ),
    ]
