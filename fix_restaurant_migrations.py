import os
import sqlite3
import sys
from pathlib import Path
import time

print("🔧 Corrigiendo dependencias de migraciones de restaurant...")

def fix_restaurant_migrations():
    """
    Corrige las dependencias de migraciones de restaurant
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
        
        # 1. Verificar migraciones existentes de restaurant
        cursor.execute("SELECT id, name, applied FROM django_migrations WHERE app = 'restaurant' ORDER BY name")
        restaurant_migrations = cursor.fetchall()
        
        print(f"📋 Migraciones de restaurant actuales:")
        for migration in restaurant_migrations:
            print(f"  - {migration[1]} (ID: {migration[0]}, Aplicada: {migration[2]})")
        
        # 2. Verificar si existe la migración fix_receta_cascade
        cursor.execute("SELECT id FROM django_migrations WHERE app = 'restaurant' AND name = 'fix_receta_cascade'")
        if not cursor.fetchone():
            # Agregar la migración faltante fix_receta_cascade
            # Se agrega con una fecha anterior a 0003_merge_20250701_1556
            cursor.execute("""
            SELECT applied FROM django_migrations 
            WHERE app = 'restaurant' AND name = '0003_merge_20250701_1556'
            """)
            merge_applied = cursor.fetchone()
            
            if merge_applied:
                # Calcular una fecha anterior
                cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('restaurant', 'fix_receta_cascade', datetime(?, '-1 hour'))
                """, (merge_applied[0],))
                conn.commit()
                print("✅ Agregada migración restaurant.fix_receta_cascade con fecha anterior")
            else:
                # Si no existe la migración merge, simplemente la agregamos
                cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('restaurant', 'fix_receta_cascade', datetime('now', '-1 day'))
                """)
                conn.commit()
                print("✅ Agregada migración restaurant.fix_receta_cascade")
        else:
            # Verificar que fix_receta_cascade esté antes que 0003_merge_20250701_1556
            cursor.execute("""
            SELECT m1.applied as fix_applied, m2.applied as merge_applied
            FROM django_migrations m1, django_migrations m2
            WHERE m1.app = 'restaurant' AND m1.name = 'fix_receta_cascade'
            AND m2.app = 'restaurant' AND m2.name = '0003_merge_20250701_1556'
            """)
            result = cursor.fetchone()
            
            if result and result[0] >= result[1]:
                # La migración fix_receta_cascade está después o al mismo tiempo que 0003_merge
                # Actualizar la fecha de fix_receta_cascade para que sea anterior
                cursor.execute("""
                UPDATE django_migrations
                SET applied = datetime(?, '-1 hour')
                WHERE app = 'restaurant' AND name = 'fix_receta_cascade'
                """, (result[1],))
                conn.commit()
                print("✅ Actualizada fecha de restaurant.fix_receta_cascade para que sea anterior a 0003_merge_20250701_1556")
            else:
                print("ℹ️ La migración restaurant.fix_receta_cascade ya tiene una fecha anterior correcta")
        
        # 3. Verificar el estado final
        cursor.execute("""
        SELECT name, applied 
        FROM django_migrations 
        WHERE app = 'restaurant' 
        ORDER BY applied, name
        """)
        final_migrations = cursor.fetchall()
        
        print("\n📋 Estado final de migraciones de restaurant:")
        for migration in final_migrations:
            print(f"  - {migration[0]} ({migration[1]})")
        
        conn.close()
        print("\n✅ Corrección de migraciones de restaurant completada")
        
        print("""
🚀 Ahora intenta ejecutar:

1. Activa tu entorno virtual:
   .\venv\Scripts\Activate.ps1

2. Ejecuta makemigrations y migrate:
   python manage.py makemigrations
   python manage.py migrate --fake-initial

3. Si continúan los problemas con restaurant, intenta:
   python manage.py migrate restaurant --fake

4. Finalmente ejecuta el servidor:
   python manage.py runserver
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_restaurant_migrations()
