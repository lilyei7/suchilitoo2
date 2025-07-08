#!/usr/bin/env python
import sqlite3
import os

# Connect to the database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"All tables: {[table[0] for table in tables]}")
        
        # Look for OrdenItem related tables
        ordenitem_tables = [table[0] for table in tables if 'ordenitem' in table[0].lower()]
        print(f"OrdenItem related tables: {ordenitem_tables}")
        
        # Check the specific table
        if 'mesero_ordenitem' in [table[0] for table in tables]:
            print("\n=== mesero_ordenitem table structure ===")
            cursor.execute("PRAGMA table_info(mesero_ordenitem)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) - NOT NULL: {bool(col[3])}")
            
            # Check if subtotal column exists and is NOT NULL
            subtotal_col = next((col for col in columns if col[1] == 'subtotal'), None)
            if subtotal_col:
                print(f"\nSubtotal column found: {subtotal_col}")
                print(f"NOT NULL constraint: {bool(subtotal_col[3])}")
            else:
                print("\nNo subtotal column found in database")
        else:
            print("mesero_ordenitem table not found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
else:
    print("Database file not found")
