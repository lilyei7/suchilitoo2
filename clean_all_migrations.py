import os
import sqlite3
import sys
from pathlib import Path

print("🧹 Limpiando completamente las migraciones...")

def clean_all_migrations():
    """
    Elimina todas las migraciones y prepara la base de datos para un --fake-initial limpio
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
        
        # 1. Backup de migraciones si no existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations_master_backup'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE django_migrations_master_backup AS 
            SELECT * FROM django_migrations
            """)
            conn.commit()
            print("✅ Backup maestro de migraciones creado")
            
        # 2. Limpiar tabla de migraciones
        cursor.execute("DELETE FROM django_migrations")
        conn.commit()
        print("🧹 Tabla django_migrations limpiada")
        
        # 3. Verificar la estructura de django_content_type
        cursor.execute("PRAGMA table_info(django_content_type)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Añadir columna name si no existe
        if 'name' not in column_names:
            cursor.execute("ALTER TABLE django_content_type ADD COLUMN name varchar(100) NULL")
            conn.commit()
            print("✅ Columna 'name' añadida a django_content_type")
        
        # 4. Insertar migraciones iniciales en el orden correcto
        migrations_order = [
            ('contenttypes', '0001_initial'),
            ('auth', '0001_initial'),
            ('accounts', '0001_initial'),
            ('admin', '0001_initial'),
            ('admin', '0002_logentry_remove_auto_add'),
            ('admin', '0003_logentry_add_action_flag_choices'),
            ('contenttypes', '0002_remove_content_type_name'),
            ('auth', '0002_alter_permission_name_max_length'),
            ('auth', '0003_alter_user_email_max_length'),
            ('auth', '0004_alter_user_username_opts'),
            ('auth', '0005_alter_user_last_login_null'),
            ('auth', '0006_require_contenttypes_0002'),
            ('auth', '0007_alter_validators_add_error_messages'),
            ('auth', '0008_alter_user_username_max_length'),
            ('auth', '0009_alter_user_last_name_max_length'),
            ('auth', '0010_alter_group_name_max_length'),
            ('auth', '0011_update_proxy_permissions'),
            ('auth', '0012_alter_user_first_name_max_length'),
            ('sessions', '0001_initial'),
            ('restaurant', '0001_initial'),
            ('restaurant', '0002_productoventa_calorias_productoreceta'),
            ('restaurant', '0003_merge_20250701_1556'),
            ('dashboard', '0001_initial'),
            ('dashboard', '0002_proveedor_creado_por_proveedor_sucursal'),
            ('dashboard', '0003_historialprecios'),
            ('dashboard', '0004_cliente_cajaapertura_cajacierre_mesa_orden_ordenitem_and_more'),
            ('dashboard', '0005_croquislayout'),
            ('dashboard', '0008_incidentcomment'),
            ('mesero', '0001_initial'),
            ('mesero', '0002_inicial'),
            ('mesero', '0003_alter_orden_mesa'),
            ('mesero', '0004_remove_ordenitem_opciones_and_more'),
            ('mesero', '0005_remove_opcionpersonalizacion_tipo_personalizacion_and_more'),
            ('mesero', '0006_ordenitem_subtotal'),
            ('cocina', '0001_initial'),
        ]
        
        # Insertar migraciones en orden
        for i, (app, name) in enumerate(migrations_order):
            # Calcula una fecha de aplicación que mantiene el orden
            applied_time = f'2025-07-15 {10 + i//60:02d}:{i%60:02d}:00'
            
            cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES (?, ?, ?)
            """, (app, name, applied_time))
        
        conn.commit()
        print(f"✅ {len(migrations_order)} migraciones básicas insertadas en orden")
        
        # 5. Verificar y crear tablas fundamentales si no existen
        essential_tables = {
            'django_migrations': 'CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL)',
            'django_content_type': 'CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL, "name" varchar(100) NULL)',
            'auth_permission': 'CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL)',
            'auth_group': 'CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE)',
            'auth_group_permissions': 'CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED)',
            'django_admin_log': 'CREATE TABLE "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action_time" datetime NOT NULL, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL, "action_flag" smallint NOT NULL CHECK ("action_flag" >= 0))',
            'django_session': 'CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL)'
        }
        
        for table_name, create_sql in essential_tables.items():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                cursor.execute(create_sql)
                conn.commit()
                print(f"✅ Tabla {table_name} creada")
        
        conn.close()
        
        print("""
🚀 La base de datos ha sido preparada. Ahora:

1. Activa tu entorno virtual:
   .\venv\Scripts\Activate.ps1

2. Ejecuta el servidor:
   python manage.py runserver
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    clean_all_migrations()
