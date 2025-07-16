from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_fix_migration_chain'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incidentreport',
            name='has_evidence',
        ),
    ]
