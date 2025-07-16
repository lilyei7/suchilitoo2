import os
import sqlite3
import sys

# Set the path to your SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')

def fix_migration_database():
    # SQL commands to run
    SQL_COMMANDS = """
    -- First remove all dashboard migrations
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
    ('dashboard', '0008_fix_migration_chain', datetime('now')),
    ('dashboard', '0009_remove_has_evidence_field', datetime('now')),
    ('dashboard', '0010_incidentevidence', datetime('now')),
    ('dashboard', '0011_incidenthistory', datetime('now'));
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
        print("\nMigration state fixed. Now run:\n  python manage.py migrate --fake")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_migration_database()
