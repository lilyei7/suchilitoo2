import os
import sqlite3
import sys
from pathlib import Path
import time

print("🔧 Corrigiendo dependencias de migraciones de mesero...")

def fix_mesero_migrations():
    """
    Corrige las dependencias de migraciones de mesero
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
        
        # Lista de dependencias a corregir
        dependencies = [
            # dependiente, requerida
            ('0003_alter_orden_mesa', '0002_auto_20250702_1652'),
            ('0005_remove_opcionpersonalizacion_tipo_personalizacion_and_more', '0004_tipopersonalizacion_alter_orden_mesa_and_more')
        ]
        
        # 1. Verificar migraciones existentes de mesero
        cursor.execute("SELECT id, name, applied FROM django_migrations WHERE app = 'mesero' ORDER BY name")
        mesero_migrations = cursor.fetchall()
        
        print(f"📋 Migraciones de mesero actuales:")
        for migration in mesero_migrations:
            print(f"  - {migration[1]} (ID: {migration[0]}, Aplicada: {migration[2]})")
        
        # 2. Procesar cada dependencia
        for dependency in dependencies:
            dependent, required = dependency
            
            # Verificar si existe la migración requerida
            cursor.execute(f"SELECT id FROM django_migrations WHERE app = 'mesero' AND name = '{required}'")
            if not cursor.fetchone():
                # Agregar la migración faltante
                # Se agrega con una fecha anterior a la dependiente
                cursor.execute(f"""
                SELECT applied FROM django_migrations 
                WHERE app = 'mesero' AND name = '{dependent}'
                """)
                dependent_applied = cursor.fetchone()
                
                if dependent_applied:
                    # Calcular una fecha anterior
                    cursor.execute(f"""
                    INSERT INTO django_migrations (app, name, applied)
                    VALUES ('mesero', '{required}', datetime(?, '-1 hour'))
                    """, (dependent_applied[0],))
                    conn.commit()
                    print(f"✅ Agregada migración mesero.{required} con fecha anterior a {dependent}")
                else:
                    # Si no existe la migración dependiente, simplemente la agregamos con fecha antigua
                    cursor.execute(f"""
                    INSERT INTO django_migrations (app, name, applied)
                    VALUES ('mesero', '{required}', datetime('now', '-1 day'))
                    """)
                    conn.commit()
                    print(f"✅ Agregada migración mesero.{required}")
            else:
                # Verificar que la requerida esté antes que la dependiente
                cursor.execute(f"""
                SELECT m1.applied as required_applied, m2.applied as dependent_applied
                FROM django_migrations m1, django_migrations m2
                WHERE m1.app = 'mesero' AND m1.name = '{required}'
                AND m2.app = 'mesero' AND m2.name = '{dependent}'
                """)
                result = cursor.fetchone()
                
                if result and result[0] >= result[1]:
                    # La migración requerida está después o al mismo tiempo que la dependiente
                    # Actualizar la fecha de la requerida para que sea anterior
                    cursor.execute(f"""
                    UPDATE django_migrations
                    SET applied = datetime(?, '-1 hour')
                    WHERE app = 'mesero' AND name = '{required}'
                    """, (result[1],))
                    conn.commit()
                    print(f"✅ Actualizada fecha de mesero.{required} para que sea anterior a {dependent}")
                else:
                    print(f"ℹ️ La migración mesero.{required} ya tiene una fecha anterior correcta a {dependent}")
        
        # 3. Verificar el estado final
        cursor.execute("""
        SELECT name, applied 
        FROM django_migrations 
        WHERE app = 'mesero' 
        ORDER BY applied, name
        """)
        final_migrations = cursor.fetchall()
        
        print("\n📋 Estado final de migraciones de mesero:")
        for migration in final_migrations:
            print(f"  - {migration[0]} ({migration[1]})")
        
        conn.close()
        print("\n✅ Corrección de migraciones de mesero completada")
        
        print("""
🚀 Ahora intenta ejecutar:

1. Activa tu entorno virtual:
   .\venv\Scripts\Activate.ps1

2. Ejecuta makemigrations y migrate:
   python manage.py makemigrations
   python manage.py migrate --fake-initial

3. Si continúan los problemas con mesero, intenta:
   python manage.py migrate mesero --fake

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
    fix_mesero_migrations()
