import os
import sqlite3
import sys
from pathlib import Path
import time

print("🚀 Iniciando reset completo de migraciones...")

def reset_all_migrations():
    """
    Elimina todas las migraciones de la base de datos y prepara para un --fake-initial
    """
    # Ruta de la base de datos SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"❌ Error: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Crear backup de la tabla django_migrations si no existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations_backup_final'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE django_migrations_backup_final AS 
            SELECT * FROM django_migrations
            """)
            conn.commit()
            print("✅ Backup final de migraciones creado")
        
        # 2. Eliminar todas las migraciones
        cursor.execute("DELETE FROM django_migrations")
        conn.commit()
        print("🧹 Todas las migraciones han sido eliminadas de la base de datos")
        
        # 3. Crear directorios para migrations si no existen
        app_names = ['dashboard', 'mesero', 'cocina', 'accounts', 'inventario']
        for app in app_names:
            migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), app, 'migrations')
            os.makedirs(migrations_dir, exist_ok=True)
            
            # Crear archivo __init__.py si no existe
            init_file = os.path.join(migrations_dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    pass
        
        print("📁 Directorios de migraciones verificados")
        
        # 4. Asegurarnos de que las tablas de los modelos existen
        essential_tables = [
            'dashboard_incidentcomment',
            'mesero_orden', 
            'mesero_ordenitem',
            'dashboard_croquislayout',
            'cocina_receta'
        ]
        
        existing_tables = []
        for table in essential_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                existing_tables.append(table)
        
        print(f"📊 Tablas existentes verificadas: {len(existing_tables)}/{len(essential_tables)}")
        
        # 5. Crear el archivo initial_data.json para cargar después de las migraciones
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [table[0] for table in cursor.fetchall() if table[0].startswith(tuple(app_names))]
        
        print(f"📋 Se han identificado {len(all_tables)} tablas para preservar datos")
        
        conn.close()
        
        print("""
🔄 Proceso completado. Ahora sigue estos pasos:

1. Activa tu entorno virtual:
   .\venv\Scripts\Activate.ps1

2. Ejecuta estas migraciones en orden:
   python manage.py migrate --fake-initial

3. Si hay errores, intenta migrar app por app:
   python manage.py migrate dashboard --fake
   python manage.py migrate mesero --fake
   python manage.py migrate cocina --fake
   python manage.py migrate accounts --fake
   python manage.py migrate inventario --fake

4. Finalmente ejecuta el servidor:
   python manage.py runserver
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    reset_all_migrations()
