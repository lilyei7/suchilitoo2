import sqlite3
import os

# Path to the database
db_path = 'db.sqlite3'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table schema for CategoriaProducto
    print("=== CategoriaProducto Table Schema ===")
    cursor.execute("PRAGMA table_info(restaurant_categoriaproducto)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"{column[1]} - {column[2]} - {'NOT NULL' if column[3] else 'NULL'}")
    
    print("\n=== Receta Table Schema ===")
    cursor.execute("PRAGMA table_info(restaurant_receta)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"{column[1]} - {column[2]} - {'NOT NULL' if column[3] else 'NULL'}")
        
    print("\n=== Inventario Table Schema ===")
    cursor.execute("PRAGMA table_info(restaurant_inventario)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"{column[1]} - {column[2]} - {'NOT NULL' if column[3] else 'NULL'}")
    
    conn.close()
else:
    print("Database file not found!")
