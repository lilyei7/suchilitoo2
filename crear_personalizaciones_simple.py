#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

import sqlite3

def create_simple_personalization_data():
    """Create simple personalization data directly in SQLite"""
    print("Creating simple personalization data...")
    
    db_path = 'db.sqlite3'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, clear existing data
        cursor.execute("DELETE FROM mesero_productopersonalizacion")
        cursor.execute("DELETE FROM mesero_opcionpersonalizacion")
        
        # Create simple options
        options = [
            ("Sin cebolla", "omitir", "vegetales", 0.00),
            ("Sin cilantro", "omitir", "vegetales", 0.00),
            ("Extra aguacate", "agregar", "extras", 2.00),
            ("Extra salmón", "agregar", "proteinas", 4.00),
            ("Salsa picante", "agregar", "salsas", 0.50),
            ("Menos picante", "modificar", "preparacion", 0.00),
        ]
        
        for i, (nombre, tipo, categoria, precio_extra) in enumerate(options, 1):
            cursor.execute("""
                INSERT INTO mesero_opcionpersonalizacion 
                (id, nombre, tipo, categoria, precio_extra, activa) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (i, nombre, tipo, categoria, precio_extra, 1))
        
        # Assign options to products (first 5 products)
        cursor.execute("SELECT id FROM restaurant_productoventa WHERE disponible = 1 LIMIT 5")
        productos = cursor.fetchall()
        
        assignment_id = 1
        for producto_id, in productos:
            # Assign 3 basic options to each product
            for opcion_id in [1, 2, 3]:  # Sin cebolla, Sin cilantro, Extra aguacate
                cursor.execute("""
                    INSERT INTO mesero_productopersonalizacion 
                    (id, producto_id, opcion_id, activa) 
                    VALUES (?, ?, ?, ?)
                """, (assignment_id, producto_id, opcion_id, 1))
                assignment_id += 1
        
        conn.commit()
        print("✓ Simple personalization data created successfully!")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM mesero_opcionpersonalizacion")
        opciones_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM mesero_productopersonalizacion")
        asignaciones_count = cursor.fetchone()[0]
        
        print(f"  - {opciones_count} personalization options created")
        print(f"  - {asignaciones_count} product assignments created")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating data: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    create_simple_personalization_data()
