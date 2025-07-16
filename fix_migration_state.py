import os
import django
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suchilitoo2.settings")
django.setup()

# Import Django models
from django.db import connection

# Clear migration records for dashboard app
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM django_migrations WHERE app = 'dashboard'")
    print("Deleted all migration records for dashboard app")
    
    # Manually add back the migrations we know are applied
    # Add migration records in the correct order
    migrations = [
        ('dashboard', '0001_initial'),
        ('dashboard', '0002_proveedor_creado_por_proveedor_sucursal'),
        ('dashboard', '0003_historialprecios'),
        ('dashboard', '0004_cliente_cajaapertura_cajacierre_mesa_orden_ordenitem_and_more'),
        ('dashboard', '0005_croquislayout'),
        ('dashboard', '0006_rename_activo_mesa_activa'),
        ('dashboard', '0007_checklistcategory_checklisttask_incidentreport_and_more'),
    ]
    
    for app, name in migrations:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, datetime('now'))",
            [app, name]
        )
        print(f"Added migration record for {app}.{name}")

print("\nMigration state fixed. Now run:\n  python manage.py migrate")
