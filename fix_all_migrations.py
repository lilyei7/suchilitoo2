import os
import sqlite3
import sys
from pathlib import Path
import time

print("Fixing all migration dependencies...")

def fix_all_migration_dependencies():
    """
    Arregla todas las dependencias de migraciones en la base de datos
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
        
        # 1. Backup de la tabla django_migrations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS django_migrations_backup AS 
        SELECT * FROM django_migrations
        """)
        conn.commit()
        print("✅ Backup de migraciones creado")
        
        # 2. Obtener todas las migraciones actuales
        cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
        all_migrations = cursor.fetchall()
        print(f"Total de migraciones: {len(all_migrations)}")
        
        # 3. Identificar y corregir dependencias
        dependency_fixes = [
            # Asegurarse de que dashboard.0005_croquislayout se aplica antes que mesero.0003_alter_orden_mesa
            ('mesero', '0003_alter_orden_mesa', 'dashboard', '0005_croquislayout'),
            # Asegurarse de que mesero.0006_ordenitem_subtotal se aplica antes que cocina.0001_initial
            ('cocina', '0001_initial', 'mesero', '0006_ordenitem_subtotal'),
            # Asegurarse de que dashboard.0004_cliente_cajaapertura... se aplica antes que dashboard.0005_croquislayout
            ('dashboard', '0005_croquislayout', 'dashboard', '0004_cliente_cajaapertura_cajacierre_mesa_orden_ordenitem_and_more'),
        ]
        
        for dep in dependency_fixes:
            dependent_app, dependent_name, required_app, required_name = dep
            
            # Comprobar si la migración dependiente existe
            cursor.execute(
                "SELECT id FROM django_migrations WHERE app = ? AND name = ?", 
                (dependent_app, dependent_name)
            )
            dependent_migration = cursor.fetchone()
            
            # Comprobar si la migración requerida existe
            cursor.execute(
                "SELECT id FROM django_migrations WHERE app = ? AND name = ?", 
                (required_app, required_name)
            )
            required_migration = cursor.fetchone()
            
            if dependent_migration and not required_migration:
                # La migración dependiente existe pero la requerida no
                # Agregar la migración requerida
                print(f"📝 Agregando migración requerida {required_app}.{required_name}")
                cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES (?, ?, datetime('now', '-1 hour'))
                """, (required_app, required_name))
                conn.commit()
            
            elif dependent_migration and required_migration:
                # Ambas migraciones existen, verificar orden
                cursor.execute(
                    "SELECT applied FROM django_migrations WHERE app = ? AND name = ?", 
                    (dependent_app, dependent_name)
                )
                dependent_time = cursor.fetchone()[0]
                
                cursor.execute(
                    "SELECT applied FROM django_migrations WHERE app = ? AND name = ?", 
                    (required_app, required_name)
                )
                required_time = cursor.fetchone()[0]
                
                if dependent_time < required_time:
                    # La dependiente se aplicó antes que la requerida
                    print(f"🔄 Corrigiendo orden: {required_app}.{required_name} debe ir antes que {dependent_app}.{dependent_name}")
                    
                    # Actualizar tiempo de la requerida para que sea anterior
                    cursor.execute("""
                    UPDATE django_migrations 
                    SET applied = datetime(?, '-1 minute')
                    WHERE app = ? AND name = ?
                    """, (dependent_time, required_app, required_name))
                    conn.commit()
        
        # 4. Arreglar caso específico de IncidentComment
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_incidentcomment'")
        if not cursor.fetchone():
            print("🔧 Creando tabla dashboard_incidentcomment")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "dashboard_incidentcomment" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "text" text NOT NULL,
                "created_at" datetime NOT NULL,
                "incident_id" integer NOT NULL REFERENCES "dashboard_incidentreport" ("id") DEFERRABLE INITIALLY DEFERRED,
                "user_id" integer NULL REFERENCES "accounts_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
            )
            """)
            
            # Crear índices
            cursor.execute('CREATE INDEX IF NOT EXISTS "dashboard_incidentcomment_incident_id_idx" ON "dashboard_incidentcomment" ("incident_id")')
            cursor.execute('CREATE INDEX IF NOT EXISTS "dashboard_incidentcomment_user_id_idx" ON "dashboard_incidentcomment" ("user_id")')
            
            # Registrar la migración
            cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('dashboard', '0008_incidentcomment', datetime('now'))
            """)
            
            conn.commit()
            print("✅ Tabla dashboard_incidentcomment creada")
        
        # 5. Mostrar el estado final de las migraciones
        cursor.execute("""
        SELECT app, name, applied FROM django_migrations 
        WHERE app IN ('dashboard', 'mesero', 'cocina')
        ORDER BY applied, app, name
        """)
        migrations = cursor.fetchall()
        print("\n🔍 Estado final de migraciones:")
        for migration in migrations:
            print(f"- {migration[0]}.{migration[1]} ({migration[2]})")
        
        conn.close()
        print("\n✅ Corrección de dependencias completada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_all_migration_dependencies()
    print("\n⏳ Esperando 3 segundos antes de continuar...")
    time.sleep(3)
    print("\n🚀 Ahora puedes ejecutar 'python manage.py migrate' para aplicar todas las migraciones")
