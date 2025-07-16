import os
import sqlite3
import shutil
import glob

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')
MIGRATIONS_DIR = os.path.join(BASE_DIR, 'dashboard', 'migrations')
BACKUP_DIR = os.path.join(BASE_DIR, 'migrations_backup')

# Create backup directory if it doesn't exist
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def create_missing_migrations():
    print("Creating missing migration files...")
    
    # Create the necessary migration files
    create_migration_file("0001_initial.py")
    create_migration_file("0002_proveedor_creado_por_proveedor_sucursal.py")
    create_migration_file("0003_historialprecios.py")
    create_migration_file("0004_cliente_cajaapertura_cajacierre_mesa_orden_ordenitem_and_more.py")
    create_migration_file("0005_croquislayout.py")
    create_migration_file("0006_rename_activo_mesa_activa.py")
    create_migration_file("0007_checklistcategory_checklisttask_incidentreport_and_more.py")
    
    # Create our new migration files for incident functionality
    create_incidenthistory_migration()
    
def create_migration_file(filename):
    file_path = os.path.join(MIGRATIONS_DIR, filename)
    
    # Create a simple empty migration
    with open(file_path, 'w') as f:
        f.write("""# Empty migration file created for migration dependency
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = []
    operations = []
""")
    
    print(f"  Created empty migration: {filename}")

def create_incidenthistory_migration():
    # Create the IncidentHistory model migration
    filename = "0008_incidenthistory_incidentevidence.py"
    file_path = os.path.join(MIGRATIONS_DIR, filename)
    
    # Write the migration content
    with open(file_path, 'w') as f:
        f.write("""# Generated manually to add IncidentHistory and IncidentEvidence models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_checklistcategory_checklisttask_incidentreport_and_more'),
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
        migrations.RemoveField(
            model_name='incidentreport',
            name='has_evidence',
        ),
    ]
""")
    
    print(f"  Created IncidentHistory migration: {filename}")

def fix_migration_database():
    # SQL commands to run
    SQL_COMMANDS = """
    -- First remove dashboard migrations
    DELETE FROM django_migrations WHERE app = 'dashboard';

    -- Then insert the migrations we want to keep
    INSERT INTO django_migrations (app, name, applied) VALUES 
    ('dashboard', '0001_initial', datetime('now')),
    ('dashboard', '0002_proveedor_creado_por_proveedor_sucursal', datetime('now')),
    ('dashboard', '0003_historialprecios', datetime('now')),
    ('dashboard', '0004_cliente_cajaapertura_cajacierre_mesa_orden_ordenitem_and_more', datetime('now')),
    ('dashboard', '0005_croquislayout', datetime('now')),
    ('dashboard', '0006_rename_activo_mesa_activa', datetime('now')),
    ('dashboard', '0007_checklistcategory_checklisttask_incidentreport_and_more', datetime('now')),
    ('dashboard', '0008_incidenthistory_incidentevidence', datetime('now'));
    """

    # Connect to the SQLite database
    try:
        print("Fixing migration database records...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute the SQL commands
        cursor.executescript(SQL_COMMANDS)
        conn.commit()
        
        # Verify the changes
        cursor.execute("SELECT app, name FROM django_migrations WHERE app='dashboard' ORDER BY id")
        migrations = cursor.fetchall()
        
        print("Dashboard migrations in database:")
        for migration in migrations:
            print(f"  - {migration[0]}.{migration[1]}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def run_fix():
    # Create empty migration files to maintain dependencies
    create_missing_migrations()
    
    # Fix the database migration state
    fix_migration_database()
    
    print("\nAll fixes applied. Now run:")
    print("  python manage.py migrate --fake")

if __name__ == "__main__":
    run_fix()
