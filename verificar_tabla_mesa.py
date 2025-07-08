#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla Mesa
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connection

def main():
    print("=== VERIFICANDO ESTRUCTURA DE TABLA MESA ===\n")
    
    cursor = connection.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='mesero_mesa';
    """)
    
    result = cursor.fetchone()
    if result:
        print("✅ Tabla 'mesero_mesa' existe")
        
        # Obtener estructura de la tabla
        cursor.execute("PRAGMA table_info(mesero_mesa);")
        columns = cursor.fetchall()
        
        print("\n📋 COLUMNAS DE LA TABLA:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Verificar si existe la columna 'estado'
        column_names = [col[1] for col in columns]
        if 'estado' in column_names:
            print("\n✅ Campo 'estado' existe en la tabla")
        else:
            print("\n❌ Campo 'estado' NO existe en la tabla")
            print("   Necesitamos agregar el campo manualmente")
    else:
        print("❌ Tabla 'mesero_mesa' NO existe")
        print("   Necesitamos ejecutar las migraciones")

if __name__ == '__main__':
    main()
