import os
import sqlite3
import sys
from pathlib import Path

print("🔧 Corrigiendo índices en la base de datos...")

def fix_indexes():
    """
    Corrige los índices problemáticos en la base de datos
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
        
        # 1. Verificar si existe el índice problemático
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='dashboard_incidentevidence_incident_report_id'")
        if cursor.fetchone():
            # Eliminar el índice
            cursor.execute("DROP INDEX dashboard_incidentevidence_incident_report_id")
            conn.commit()
            print("✅ Índice problemático eliminado")
        else:
            print("ℹ️ El índice problemático no existe")
            
        # 2. Verificar si existe la tabla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_incidentevidence'")
        if cursor.fetchone():
            # Obtener la estructura de la tabla
            cursor.execute("PRAGMA table_info(dashboard_incidentevidence)")
            columns = cursor.fetchall()
            
            # Imprimir la estructura
            print(f"\n📋 Estructura de la tabla dashboard_incidentevidence:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                
            # Verificar si existe la columna incident_report_id
            has_column = any(col[1] == 'incident_report_id' for col in columns)
            
            if not has_column:
                # Crear columna si no existe
                cursor.execute("ALTER TABLE dashboard_incidentevidence ADD COLUMN incident_report_id integer NULL REFERENCES dashboard_incidentreport(id)")
                conn.commit()
                print("✅ Columna incident_report_id añadida")
                
                # Recrear el índice
                cursor.execute("CREATE INDEX dashboard_incidentevidence_incident_report_id ON dashboard_incidentevidence(incident_report_id)")
                conn.commit()
                print("✅ Índice recreado")
            else:
                print("ℹ️ La columna incident_report_id ya existe")
        else:
            print("ℹ️ La tabla dashboard_incidentevidence no existe")
            
        # 3. Mostrar todos los índices para verificar
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'dashboard_%'")
        indices = cursor.fetchall()
        
        print(f"\n📋 Índices de dashboard:")
        for idx in indices:
            print(f"  - {idx[0]}")
            
        conn.close()
        print("\n✅ Corrección de índices completada")
        
        print("""
🚀 Ahora intenta aplicar las migraciones app por app:

1. Activa tu entorno virtual:
   .\venv\Scripts\Activate.ps1

2. Ejecuta estas migraciones en orden:
   python manage.py migrate auth --fake
   python manage.py migrate contenttypes --fake
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
    fix_indexes()
