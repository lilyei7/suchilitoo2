import os
import sys
import sqlite3

def fix_migration_order():
    """
    Corrige el orden de las migraciones en la base de datos
    """
    # Ruta de la base de datos SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"Error: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener el ID de la migración dashboard.0005_croquislayout
        cursor.execute("SELECT id FROM django_migrations WHERE app = 'dashboard' AND name = '0005_croquislayout'")
        dashboard_migration = cursor.fetchone()
        
        if not dashboard_migration:
            print("Error: La migración dashboard.0005_croquislayout no se encuentra en la base de datos.")
            
            # Insertar la migración manualmente
            cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('dashboard', '0005_croquislayout', datetime('now'))
            """)
            conn.commit()
            print("Migración dashboard.0005_croquislayout agregada manualmente.")
        else:
            print(f"La migración dashboard.0005_croquislayout ya existe (ID: {dashboard_migration[0]})")
        
        # Verificar que todas las migraciones de dashboard estén aplicadas hasta la 0005_croquislayout
        cursor.execute("SELECT name FROM django_migrations WHERE app = 'dashboard' ORDER BY name")
        dashboard_migrations = cursor.fetchall()
        print("\nMigraciones de dashboard aplicadas:")
        for migration in dashboard_migrations:
            print(f"- {migration[0]}")
        
        # Eliminar todas las migraciones de mesero
        cursor.execute("DELETE FROM django_migrations WHERE app = 'mesero'")
        conn.commit()
        print("\nMigraciones de mesero eliminadas de la base de datos.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error al arreglar migraciones: {e}")
        return False

if __name__ == "__main__":
    fix_migration_order()
    print("\nAhora puedes ejecutar los siguientes comandos para aplicar correctamente las migraciones:")
    print("1. python manage.py migrate dashboard")
    print("2. python manage.py migrate mesero")
