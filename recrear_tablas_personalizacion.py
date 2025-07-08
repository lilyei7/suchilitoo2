#!/usr/bin/env python3
import os
import sys
import sqlite3

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

def recreate_personalization_tables():
    """Recreate the personalization tables directly in SQLite"""
    db_path = 'db.sqlite3'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS mesero_ordenitempersonalizacion")
        cursor.execute("DROP TABLE IF EXISTS mesero_productopersonalizacion")
        cursor.execute("DROP TABLE IF EXISTS mesero_opcionpersonalizacion")
        cursor.execute("DROP TABLE IF EXISTS mesero_tipopersonalizacion")
        
        # Create OpcionPersonalizacion table
        cursor.execute("""
            CREATE TABLE mesero_opcionpersonalizacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                precio_extra DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                activa BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        
        # Create ProductoPersonalizacion table
        cursor.execute("""
            CREATE TABLE mesero_productopersonalizacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                opcion_id INTEGER NOT NULL,
                activa BOOLEAN NOT NULL DEFAULT 1,
                FOREIGN KEY (producto_id) REFERENCES restaurant_productoventa(id),
                FOREIGN KEY (opcion_id) REFERENCES mesero_opcionpersonalizacion(id)
            )
        """)
        
        # Create OrdenItemPersonalizacion table
        cursor.execute("""
            CREATE TABLE mesero_ordenitempersonalizacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_item_id INTEGER NOT NULL,
                opcion_id INTEGER NOT NULL,
                valor TEXT,
                precio_aplicado DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                FOREIGN KEY (orden_item_id) REFERENCES mesero_ordenitem(id),
                FOREIGN KEY (opcion_id) REFERENCES mesero_opcionpersonalizacion(id)
            )
        """)
        
        conn.commit()
        print("✓ Tables recreated successfully")
        
        # Mark migration as applied
        cursor.execute("""
            UPDATE django_migrations 
            SET applied = datetime('now') 
            WHERE app = 'mesero' AND name = '0005_remove_opcionpersonalizacion_tipo_personalizacion_and_more'
        """)
        
        conn.commit()
        print("✓ Migration marked as applied")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error recreating tables: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("Recreating personalization tables...")
    success = recreate_personalization_tables()
    
    if success:
        print("\nTables recreated successfully!")
        print("Now run: python manage.py migrate")
    else:
        print("\nFailed to recreate tables")
