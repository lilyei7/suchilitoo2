import os
import sqlite3
import sys
from pathlib import Path

print("🔧 Corrigiendo estructura de django_content_type...")

def fix_content_type_table():
    """
    Corrige la estructura de la tabla django_content_type
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
        
        # 1. Verificar la estructura actual de la tabla
        cursor.execute("PRAGMA table_info(django_content_type)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Estructura actual de django_content_type:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 2. Verificar si falta la columna 'name'
        if 'name' not in column_names:
            # Crear una copia de seguridad de la tabla
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_content_type_backup AS 
            SELECT * FROM django_content_type
            """)
            conn.commit()
            print("✅ Backup de django_content_type creado")
            
            # Añadir la columna 'name'
            cursor.execute("ALTER TABLE django_content_type ADD COLUMN name varchar(100) NULL")
            conn.commit()
            print("✅ Columna 'name' añadida a django_content_type")
        else:
            print("ℹ️ La columna 'name' ya existe en django_content_type")
            
        # 3. Limpiar las migraciones de contenttypes para empezar de nuevo
        cursor.execute("DELETE FROM django_migrations WHERE app = 'contenttypes'")
        conn.commit()
        print("✅ Migraciones de contenttypes eliminadas")
        
        conn.close()
        print("\n✅ Corrección de django_content_type completada")
        
        print("""
🚀 Ahora intenta aplicar las migraciones en el siguiente orden:

1. Activa tu entorno virtual:
   .\venv\Scripts\Activate.ps1

2. Ejecuta estas migraciones en orden:
   python manage.py migrate contenttypes 0001_initial --fake
   python manage.py migrate auth --fake
   python manage.py migrate admin --fake
   python manage.py migrate sessions --fake
   python manage.py migrate accounts --fake
   python manage.py migrate dashboard --fake
   python manage.py migrate mesero --fake
   python manage.py migrate cocina --fake
   python manage.py migrate inventario --fake
   python manage.py migrate restaurant --fake

3. Finalmente ejecuta el servidor:
   python manage.py runserver
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_content_type_table()
